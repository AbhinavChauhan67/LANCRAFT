from flask import Flask, render_template, request, redirect, url_for, session
import random
import string

app = Flask(__name__)
app.secret_key = "minecraft-multiplayer-lan"

# ===== IN-MEMORY LOBBIES =====
lobbies = {}

def new_world():
    return {
        "players": {},
        "inventory": [],
        "log": ["🌲 You wake up in the wilderness."],
        "image": "explore.png",
        "game_over": False,
        "winner": None
    }

def create_lobby():
    lobby_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    lobbies[lobby_id] = new_world()
    return lobby_id

def add_player(lobby_id, pid):
    lobbies[lobby_id]["players"][pid] = {
        "health": 100,
        "stamina": 100,
        "alive": True
    }

@app.route("/")
def menu():
    return render_template("menu.html")

@app.route("/manual")
def manual():
    return render_template("manual.html")

@app.route("/multiplayer")
def multiplayer():
    return render_template("multiplayer.html")

@app.route("/create_lobby")
def create():
    lobby_id = create_lobby()
    pid = "P1"
    session["lobby"] = lobby_id
    session["pid"] = pid
    add_player(lobby_id, pid)
    return redirect(url_for("lobby"))

@app.route("/join_lobby", methods=["POST"])
def join():
    lobby_id = request.form["lobby"].upper()
    if lobby_id in lobbies and len(lobbies[lobby_id]["players"]) < 2:
        pid = "P2"
        session["lobby"] = lobby_id
        session["pid"] = pid
        add_player(lobby_id, pid)
        return redirect(url_for("lobby"))
    return "Invalid or full lobby"

@app.route("/lobby", methods=["GET", "POST"])
def lobby():
    lobby_id = session.get("lobby")
    pid = session.get("pid")

    if not lobby_id or lobby_id not in lobbies:
        return redirect("/")

    world = lobbies[lobby_id]
    me = world["players"][pid]

    if request.method == "POST" and not world["game_over"]:

        if not me["alive"]:
            world["log"].append(f"💀 {pid} is dead and can only watch.")
            return redirect(url_for("lobby"))

        cmd = request.form["command"].lower().strip()
        log = world["log"]

        # ===== EXPLORE =====
        if cmd == "explore":
            if me["stamina"] <= 0:
                log.append(f"⚠️ {pid} is too exhausted to explore. Type 'rest' to choose where to recover!")
            else:
                me["stamina"] = max(0, me["stamina"] - 20)

                # 5% chance for map → 1 out of 20
                events = (
                    [("🍓 Found berries", 0, 0, "explore.png", "berries")] * 7 +
                    [("🩹 Found bandage", 0, 0, "bandage.png", "bandage")] * 7 +
                    [("🐻 Bear attack!", -30, -40, "bear.png")] * 5 +
                    [("🗺️ Found map!", 0, 0, "map.png", "map")]
                )

                event = random.choice(events)

                log.append(f"{pid}: {event[0]}")
                me["stamina"] = min(100, me["stamina"] + event[1])
                me["health"] = max(0, me["health"] + event[2])
                world["image"] = event[3]

                # Add item to inventory if exists
                if len(event) == 5 and event[4] not in world["inventory"]:
                    world["inventory"].append(event[4])
                    log.append(f"🎒 {event[4].capitalize()} added to shared inventory")

                if me["health"] == 0:
                    me["alive"] = False
                    log.append(f"💀 {pid} has died!")

        # ===== REST =====
        elif cmd.startswith("rest"):
            parts = cmd.split()
            # Player just typed "rest" → prompt choice
            if len(parts) == 1:
                log.append(f"⚠️ {pid}, where do you want to rest? Type 'rest cave' or 'rest forest'.")
            else:
                place = parts[1]
                if place == "cave":
                    me["stamina"] = min(100, me["stamina"] + 40)
                    world["image"] = "cave.png"
                    log.append(f"💤 {pid} rests safely in the cave and recovers stamina. Current: {me['stamina']}")
                elif place == "forest":
                    world["image"] = "explore.png"  # forest image
                    damage = random.randint(20, 50)
                    me["health"] = max(0, me["health"] - damage)
                    if me["health"] == 0:
                        me["alive"] = False
                        log.append(f"🐻 {pid} tried to rest in the forest but a wild animal killed them!")
                    else:
                        log.append(f"🐻 {pid} tried to rest in the forest but was attacked by a wild animal! Lost {damage} HP. Current HP: {me['health']}")
                else:
                    log.append(f"⚠️ Invalid rest location. Type 'rest cave' or 'rest forest'.")

        # ===== USE ITEM =====
        elif cmd.startswith("use "):
            item = cmd[4:].strip()
            if item not in world["inventory"]:
                log.append(f"⚠️ {pid} does not have {item}.")
            else:
                if item == "berries":
                    me["health"] = min(100, me["health"] + 5)
                    log.append(f"🍓 {pid} eats berries and recovers 5 health. Current: {me['health']}")
                elif item == "bandage":
                    me["health"] = min(100, me["health"] + 15)
                    log.append(f"🩹 {pid} uses a bandage and recovers 15 health. Current: {me['health']}")
                world["inventory"].remove(item)

        # ===== INVENTORY =====
        elif cmd == "inventory":
            log.append("🎒 Inventory: " + ", ".join(world["inventory"]))

        # ===== CHECK WIN/LOSE CONDITIONS =====
        if not world["game_over"]:
            # Map-win
            if "map" in world["inventory"]:
                world["game_over"] = True
                world["winner"] = "ALL"
                log.append("🏆 MAP FOUND — ALL PLAYERS WIN!")
            # All players dead
            elif all(not p["alive"] for p in world["players"].values()):
                world["game_over"] = True
                world["winner"] = None
                log.append("💀 All players have died. GAME OVER!")

        world["log"] = log

    return render_template(
        "lobby.html",
        world=world,
        lobby=lobby_id,
        pid=pid
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

#end of file