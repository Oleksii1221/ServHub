import os
import threading
import time
import socket
from flask import Flask, render_template, request, send_from_directory

app = Flask(__name__)

SERVERS_DIR = "servers"
LOGO_FOLDER = "static/logos"
PING_RESULTS = {}  # server_id: ping in ms or None
DEFAULT_HOST = "127.0.0.1"  # або змінюй як потрібно

# Читання даних з .txt файлу
def load_server_config(filename):
    config = {
        "name": "Unnamed",
        "port": 0,
        "logo": "",
        "ping_interval": 30,
        "name_color": "#000000",
        "hidden": False,
        "notes": "",
        "category": "",
        "priority": 0,
        "status_override": ""
    }
    try:
        with open(os.path.join(SERVERS_DIR, filename), "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    if key in config:
                        if key == "port":
                            config[key] = int(value)
                        elif key == "ping_interval" or key == "priority":
                            config[key] = int(value)
                        elif key == "hidden":
                            config[key] = value.lower() == "true"
                        else:
                            config[key] = value
        return config
    except Exception as e:
        print(f"[ERROR] Failed to load {filename}: {e}")
        return None

def ping_server(host, port, timeout=1.0):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except:
        return False

def background_ping():
    while True:
        for filename in os.listdir(SERVERS_DIR):
            if not filename.endswith(".txt"):
                continue
            config = load_server_config(filename)
            if config and not config["hidden"]:
                host = DEFAULT_HOST
                port = config["port"]
                name = filename[:-4]
                if config["status_override"]:
                    PING_RESULTS[name] = config["status_override"]
                else:
                    if ping_server(host, port):
                        PING_RESULTS[name] = "Online"
                    else:
                        PING_RESULTS[name] = "Offline"
        time.sleep(5)

@app.route("/")
def index():
    servers = []
    host = request.host.split(":")[0]
    global DEFAULT_HOST
    DEFAULT_HOST = host  # оновлюємо хост для пінгу

    for filename in os.listdir(SERVERS_DIR):
        if filename.endswith(".txt"):
            config = load_server_config(filename)
            if config and not config["hidden"]:
                server_id = filename[:-4]
                config["status"] = PING_RESULTS.get(server_id, "Unknown")
                config["address"] = f"http://{host}:{config['port']}"
                servers.append(config)

    servers.sort(key=lambda x: x.get("priority", 0), reverse=True)
    return render_template("index.html", servers=servers)

@app.route("/static/logos/<path:filename>")
def serve_logo(filename):
    return send_from_directory(LOGO_FOLDER, filename)

if __name__ == "__main__":
    os.makedirs(SERVERS_DIR, exist_ok=True)
    os.makedirs(LOGO_FOLDER, exist_ok=True)

    # Запускаємо потік для пінгу
    threading.Thread(target=background_ping, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, debug=True)