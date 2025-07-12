import telnetlib
import threading
import json
import time
import re
import os

# Configuration
HOST = "localhost"
PORT = 8081
PASSWORD = "PasswordFromServerConfigFileForTelenetGoesHere"

DATA_FILE = "player_data.json"

# Load or initialize player data
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Send a command to the server
def send_to_server(cmd):
    print("➡️ Sending to server:", cmd)
    tn.write((cmd + "\n").encode())
    tn.write(b"\n")  # Send a second newline to flush
    tn.write(b"")    # Some Telnet servers flush on double newline
    time.sleep(0.1)  # Optional delay to ensure execution. Do not remove had issues where each command is delayed by 1 command and so all commands were working in properly

# Extract player coordinates from LP output
def get_player_location(steam_id):
    send_to_server("lp")
    start_time = time.time()

    print("⏳ Waiting for lp response...")

    while time.time() - start_time < 5:  # 5 second timeout
        try:
            line = tn.read_until(b"\n", timeout=1).decode(errors="ignore").strip()
            if not line:
                continue
            print("🔍", line)

            # ✅ Match line containing the Steam ID and pos=
            if f"pltfmid=Steam_{steam_id}" in line and "pos=" in line:
                match = re.search(r"pos=\(([-\d.]+), ([-\d.]+), ([-\d.]+)\)", line)
                if match:
                    x, y, z = match.groups()
                    print(f"📍 Found position for {steam_id}: {x}, {y}, {z}")
                    return {"x": float(x), "y": float(y), "z": float(z)}

        except Exception as e:
            print("⚠️ Error reading lp output:", e)

    print("⚠️ LP output did not include player coordinates.")
    return None

# Handle incoming chat messages
def handle_chat_line(line):
    match = re.search(r"Chat \(from 'Steam_(\d+)', entity id '(\d+)', to 'Global'\): '.*?': (/[\w]+)", line)
    if not match:
        return

    steam_id = match.group(1)
    entity_id = match.group(2)
    command = match.group(3).strip().lower()

    print(f"📬 Detected command: {command} from SteamID {steam_id}")

    data = load_data()
    player = data.get(steam_id, {})
    player["entity_id"] = entity_id
    data[steam_id] = player  # Ensure the player entry exists

    if command == "/setbase":
        loc = get_player_location(steam_id)
        if loc:
            player["base"] = loc
            send_to_server(f"say \"Base set at X: {loc['x']:.1f}, Y: {loc['y']:.1f}, Z: {loc['z']:.1f}\"")
        else:
            send_to_server(f"say \"Failed to get your current location to set base.\"")

    elif command == "/base":
        if "base" in player:
            current_loc = get_player_location(steam_id)
            if current_loc:
                player["return"] = current_loc  # Save location before teleporting
                base_loc = player["base"]
                send_to_server(f"say \"Teleporting to base at X: {base_loc['x']:.1f}, Y: {base_loc['y']:.1f}, Z: {base_loc['z']:.1f}\"")
                send_to_server(f"teleportplayer {player['entity_id']} {int(base_loc['x'])} {int(base_loc['y'])} {int(base_loc['z'])}")
            else:
                send_to_server("say \"Could not retrieve your current location before teleporting.\"")
        else:
            send_to_server("say \"No base set. Use /setbase first.\"")

    elif command == "/return":
        if "return" in player:
            ret_loc = player.pop("return")  # Remove it after use
            send_to_server(f"say \"Returning to X: {ret_loc['x']:.1f}, Y: {ret_loc['y']:.1f}, Z: {ret_loc['z']:.1f}\"")
            send_to_server(f"teleportplayer {player['entity_id']} {int(ret_loc['x'])} {int(ret_loc['y'])} {int(ret_loc['z'])}")
        else:
            send_to_server("say \"No return location saved. Use /base first.\"")

    elif command == "/help":
        send_to_server(f"say {steam_id} Commands: /setbase, /base, /return, /help")

    # Always save data at the end
    data[steam_id] = player
    save_data(data)



# Telnet listener thread
def listen_telnet():
    print("📡 Listening to server...")
    while True:
        try:
            line = tn.read_until(b"\n").decode(errors="ignore").strip()
            print("📥", line)
            if "Chat (" in line:
                handle_chat_line(line)
        except Exception as e:
            print("❌ Error reading from server:", e)
            break

# Connect to server via Telnet
print("🔌 Connecting to 7DTD server via Telnet...")
tn = telnetlib.Telnet(HOST, PORT)
tn.read_until(b"Please enter password:")
tn.write((PASSWORD + "\n").encode())
print("✅ Connected to server")

# 🧹 Flush old Telnet output
start_time = time.time()
while time.time() - start_time < 1:
    try:
        tn.read_very_eager()
    except:
        break

# Start listener thread
threading.Thread(target=listen_telnet, daemon=True).start()

# Keep the bot running
while True:
    time.sleep(1)
