import os
import configparser
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

SERVERS_DIR = "servers"
LOGOS_DIR = os.path.join("static", "logos")
ICONS_DIR = os.path.join("static", "icons")


def load_server_configs():
    servers = []
    for filename in os.listdir(SERVERS_DIR):
        if filename.endswith(".txt"):
            config = configparser.ConfigParser()
            config.read(os.path.join(SERVERS_DIR, filename), encoding='utf-8')
            if "DEFAULT" in config:
                server = dict(config["DEFAULT"])
                servers.append(server)

    # Сортування за пріоритетом (спадаюче)
    def sort_key(server):
        try:
            return int(server.get("priority", 0))
        except ValueError:
            return 0

    servers.sort(key=sort_key, reverse=True)
    return servers


@app.route("/")
def index():
    servers = load_server_configs()
    return render_template("index.html", servers=servers)


@app.route("/settings")
def settings():
    servers = load_server_configs()
    return render_template("settings.html", servers_count=len(servers))



@app.route("/updates")
def updates():
    return "<h2>Дід йобнутий тому будуть оновлення.</h2>"


@app.route("/static/logos/<path:filename>")
def logo(filename):
    return send_from_directory(LOGOS_DIR, filename)


@app.route("/static/icons/<path:filename>")
def icons(filename):
    return send_from_directory(ICONS_DIR, filename)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
