from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from collections import defaultdict

app = Flask(__name__, template_folder="templates")
CORS(app)

# MongoDB Connection
client = MongoClient("mongodb://192.168.4.118:27017/")
db = client["SuperBowl2025"]
collection = db["SuperBowl2025"]

# Home Page (Links to All Views)
@app.route("/")
def home():
    return render_template("home.html")

# Summary Page
@app.route("/summary")
def summary():
    return render_template("summary.html")

# Player Comparison Page
@app.route("/compare")
def compare():
    return render_template("compare.html")

# Performance Trends Page
@app.route("/trends")
def trends():
    return render_template("trends.html")

# API: Fetch Player Summary
@app.route("/players/summary", methods=["GET"])
def get_players_summary():
    players = list(collection.find())

    player_stats = defaultdict(lambda: {
        "Games Played": 0, "PAtt": 0, "PC": 0, "PaY": 0, "PaTD": 0, "I": 0,
        "RA": 0, "RuY": 0, "RuTD": 0, "F": 0, "Tar": 0, "Re": 0,
        "ReY": 0, "ReTD": 0, "FP": 0
    })

    for player in players:
        name, team, position = player.get("Name", "Unknown"), player.get("Team", "Unknown"), player.get("Position", "Unknown")
        key = (name, team, position)

        player_stats[key]["Games Played"] += 1
        for stat in player_stats[key].keys():
            if stat in player and isinstance(player[stat], (int, float)):
                player_stats[key][stat] += player[stat]

    summary = []
    for (name, team, position), stats in player_stats.items():
        games = stats["Games Played"]
        avg_stats = {stat: round(stats[stat] / games, 2) if games > 0 else 0 for stat in stats if stat != "Games Played"}
        summary.append({"Name": name, "Team": team, "Position": position, "Games Played": games, **avg_stats})

    return jsonify(summary)

# API: Compare Selected Players
@app.route("/players/compare", methods=["POST"])
def compare_players():
    selected_players = request.json.get("players", [])
    if not selected_players:
        return jsonify({"error": "No players selected"}), 400

    players = list(collection.find({"Name": {"$in": selected_players}}))
    if not players:
        return jsonify({"error": "Players not found"}), 404

    stats = {player["Name"]: {stat: 0 for stat in ["Games Played", "PAtt", "PC", "PaY", "PaTD", "I", "RA", "RuY", "RuTD", "F", "Tar", "Re", "ReY", "ReTD", "FP"]} for player in players}

    for player in players:
        name = player["Name"]
        stats[name]["Games Played"] += 1
        for stat in stats[name].keys():
            if stat in player and isinstance(player[stat], (int, float)):
                stats[name][stat] += player[stat]

    for name in stats:
        games = stats[name]["Games Played"]
        for stat in stats[name]:
            if stat != "Games Played" and games > 0:
                stats[name][stat] = round(stats[name][stat] / games, 2)

    return jsonify(stats)

# API: Player Performance Trends
@app.route("/players/trends/<player_name>", methods=["GET"])
def player_trends(player_name):
    players = list(collection.find({"Name": player_name}))
    if not players:
        return jsonify({"error": "Player not found"}), 404

    trends = sorted([{"date": player["DATE"], "FP": player.get("FP", 0), "PaY": player.get("PaY", 0), "RuY": player.get("RuY", 0)} for player in players], key=lambda x: x["date"])

    return jsonify(trends)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
