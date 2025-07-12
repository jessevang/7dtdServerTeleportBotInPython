# 🧭 7DTD Server Teleport Bot in Python

A lightweight Python-based teleport bot that allows players to set a base, return to it, and teleport back to their last location using in-game chat commands.

---

## 📌 Features

- `/setbase` — Saves your current location as your base
- `/base` — Teleports you to your saved base (if available)
- `/return` — Teleports you back to the last location before using `/base`
- `/help` — Displays all available commands

---

## 🛠 Requirements

- A **7 Days to Die Dedicated Server** with **Telnet enabled**
- Python 3.8+
- Admin access to configure Telnet settings
- Install Python packages (none currently required beyond standard library)

---

## ⚙️ 1. Enable Telnet on Your 7DTD Server

Edit your `serverconfig.xml` and make sure the following lines are set:

```xml
<TelnetEnabled>true</TelnetEnabled>
<TelnetPort>8081</TelnetPort>
<TelnetPassword>YourSecretPassword</TelnetPassword>
```

Restart the server after changing settings.

---

## 📁 2. Configure the Bot

In `bot.py`, update the following configuration section near the top:

```python
HOST = "localhost"  # or your server IP address
PORT = 8081         # match the Telnet port in serverconfig.xml
PASSWORD = "YourSecretPassword"  # match the TelnetPassword
```

---

## ▶️ 3. Run the Bot

From a terminal or command prompt:

```bash
python bot.py
```

You should see output like:

```
🔌 Connecting to 7DTD server via Telnet...
✅ Connected to server
📡 Listening to server...
```

---

## 💬 4. In-Game Usage

Join the game as a player and type these in global chat:

- `/setbase` — Sets your current position as your base.
- `/base` — Teleports you to your saved base.
- `/return` — Returns you to your previous position before teleporting to base.
- `/help` — Shows available commands.

⚠️ **Note:** Teleporting is **disabled during Blood Moon** by design.

---

## 🗂 Data Persistence

All player locations are saved to `player_data.json` in the same directory. Each player is tracked by Steam ID.

---

## 🔐 Security Note

Ensure your server Telnet password is strong and do **not** expose Telnet to the public internet.

---

## 📝 License

MIT License (see `LICENSE.txt`)