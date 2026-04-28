from flask import Flask, request, jsonify
import requests
import time
import os

app = Flask(__name__)

BIN_ID = "69cbf02c36566621a8675955"
JSONBIN_API_KEY = os.environ.get("JSONBIN_API_KEY")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def jsonbin_get_players():
    if not JSONBIN_API_KEY:
        return {"players": []}
    headers = {"X-Master-Key": JSONBIN_API_KEY}
    try:
        resp = requests.get(f"https://api.jsonbin.io/v3/b/{BIN_ID}", headers=headers, timeout=10)
        if resp.status_code == 200:
            return resp.json().get("record", {"players": []})
    except:
        pass
    return {"players": []}

def jsonbin_update_players(players):
    if not JSONBIN_API_KEY:
        return False
    headers = {"X-Master-Key": JSONBIN_API_KEY, "Content-Type": "application/json"}
    data = {"players": players, "count": len(players), "last_update": time.time()}
    try:
        resp = requests.put(f"https://api.jsonbin.io/v3/b/{BIN_ID}", headers=headers, json=data, timeout=10)
        return resp.status_code == 200
    except:
        return False

def send_discord(content):
    if not DISCORD_WEBHOOK_URL:
        return
    try:
        payload = {"content": content, "username": "Turbo Launcher"}
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
    except:
        pass

@app.route('/api/turbo', methods=['POST', 'OPTIONS'])
def turbo_api():
    if request.method == 'OPTIONS':
        response = jsonify({"status": "ok"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response
    
    data = request.get_json(silent=True) or {}
    action = data.get("action")
    username = data.get("username")
    
    if action == "get_players":
        players_data = jsonbin_get_players()
        response = jsonify({"success": True, "players": players_data.get("players", [])})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    if action == "player_join" and username:
        players_data = jsonbin_get_players()
        players = players_data.get("players", [])
        if username not in players:
            players.append(username)
            jsonbin_update_players(players)
            send_discord(f"**{username}** зашёл в игру! Всего: {len(players)} игроков")
        response = jsonify({"success": True, "players": players, "count": len(players)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    if action == "player_leave" and username:
        players_data = jsonbin_get_players()
        players = players_data.get("players", [])
        if username in players:
            players.remove(username)
            jsonbin_update_players(players)
        response = jsonify({"success": True, "players": players, "count": len(players)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    if action == "health":
        response = jsonify({"status": "ok", "timestamp": time.time()})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    response = jsonify({"error": "Unknown action", "success": False})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 400

app = app
