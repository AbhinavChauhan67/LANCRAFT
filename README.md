# LANCRAFT

🌲 LANCRAFT — LAN Co-op Text Survival Game

A browser-based LAN multiplayer survival game inspired by text adventures and survival mechanics.
Players cooperate in a shared world, manage health and stamina, face random events, and try to survive long enough to escape the wilderness.

🎮 Game Type

LAN Co-op Text Survival Game

Command-based gameplay

Shared world & inventory

Lightweight browser multiplayer using Flask

🧩 Gameplay Overview

You wake up lost in a dangerous forest.

No food

No shelter

Wild animals everywhere

Players must explore, manage health & stamina, and work together to survive.
The game is won when any player finds the map — even if other players are already dead.

👥 Multiplayer Rules

Maximum 2 players per lobby

Shared world, log, and inventory

Each player has:

Health

Stamina

Alive / Dead state

Death & Victory Logic

If one player dies, the other can continue

Dead players can watch but cannot act

If any alive player wins, ALL players win

📋 Commands

explore — Search for food or items (uses stamina)

inventory — View shared inventory

Survival Rules

Stamina 0 → cannot explore

Health 0 → player dies

Health and stamina never go below 0

Map is very rare to find

🛠️ Tech Stack

Backend: Python + Flask

Frontend: HTML + CSS

Multiplayer: LAN (shared server state)

No database (in-memory lobbies)
