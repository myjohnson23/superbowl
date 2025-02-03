from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from collections import defaultdict

app = Flask(__name__)
CORS(app)

# MongoDB Connection
client = MongoClient("mongodb://192.168.4.118:27017/")
db = client["SuperBowl2025"]
collection = db["SuperBowl2025"]

# Helper function to format MongoDB data
def format_document(doc):
    doc["_id"] = str(doc["_id"])
    return doc

# Serve HTML page
@app.route("/")
def index():
    return render_template("index.html")

# Fetch all players
@app.route("/players", methods=["GET"])
def get_players():
    players = list(collection.find())
    return jsonify([format_document(player) for player in players])

# Fetch a summarized view of all players with averages
@app.route("/players/summary", methods=["GET"])
def get_players_summary():
    players = list(collection.find())

    # Dictionary to store accumulated stats
    player_stats = defaultdict(lambda: {
        "Games Played": 0,
        "Pass Comp": 0, "Pass Att": 0, "Pass Yds": 0, "Pass TDs": 0, "Int": 0,
        "Rush Att": 0, "Rush Yds": 0, "Rush TDs": 0, "Fum": 0,
        "Target": 0, "Rec": 0, "Rec Yds": 0, "Rec TDs": 0,
        "Fantasy Points": 0
    })

    # Sum up stats for each player
    for player in players:
        key = (player["Name"], player["Team"], player["Position"])
        player_stats[key]["Games Played"] += 1

        for stat in ["Pass Comp", "Pass Att", "Pass Yds", "Pass TDs", "Int",
                     "Rush Att", "Rush Yds", "Rush TDs", "Fum",
                     "Target", "Rec", "Rec Yds", "Rec TDs",
                     "Fantasy Points"]:
            if stat in player and isinstance(player[stat], (int, float)):
                player_stats[key][stat] += player[stat]

    # Compute averages
    summary = []
    for (name, team, position), stats in player_stats.items():
        games_played = stats["Games Played"]
        avg_stats = {stat: round(stats[stat] / games_played, 2) if games_played > 0 else 0
                     for stat in stats if stat != "Games Played"}
        
        summary.append({
            "Name": name,
            "Team": team,
            "Position": position,
            "Games Played": games_played,
            **avg_stats
        })

    return jsonify(summary)

# Add a new player
@app.route("/players", methods=["POST"])
def add_player():
    data = request.json
    result = collection.insert_one(data)
    return jsonify({"message": "Player added", "id": str(result.inserted_id)}), 201

# Delete a player by ID
@app.route("/players/<string:player_id>", methods=["DELETE"])
def delete_player(player_id):
    result = collection.delete_one({"_id": ObjectId(player_id)})
    
    if result.deleted_count == 0:
        return jsonify({"error": "Player not found"}), 404
    return jsonify({"message": "Player deleted successfully"})

# Run Flask on all network interfaces
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
