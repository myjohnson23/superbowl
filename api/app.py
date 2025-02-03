from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
CORS(app)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017")
db = client["SuperBowl2025"]
collection = db["SuperBowl2025"]

# Helper function to convert MongoDB documents to JSON
def format_document(doc):
    doc["_id"] = str(doc["_id"])
    return doc

# Fetch all records or filter by Name/Team
@app.route("/players", methods=["GET"])
def get_players():
    name = request.args.get("name")
    team = request.args.get("team")

    query = {}
    if name: 
        query["Name"] = name
    if team:
        query["Team"] = team

    players = list(collection.find(query))
    formatted_players = [format_document(player) for player in players]

    return jsonify(formatted_players)

# Fetch a single record by ID
@app.route("/players/<string:player_id>", methods=["GET"])
def get_player(player_id):
    player = collection.find_one({"_id": ObjectId(player_id)})
    if player:
        return jsonify(format_document(player))
    return jsonify({"error": "Player not found"}), 404

# Add a new player
@app.route("/players", methods=["POST"])
def add_player():
    data = request.json
    result = collection.insert_one(data)
    return jsonify({"message": "Player added", "id": str(result.inserted_id)}), 201

# Update a player by ID
@app.route("/players/<string:player_id>", methods=["PUT"])
def update_player(player_id):
    data = request.json
    result = collection.update_one({"_id": ObjectId(player_id)}, {"$set": data})
    
    if result.matched_count == 0:
        return jsonify({"error": "Player not found"}), 404
    return jsonify({"message": "Player updated successfully"})

# Delete a player by ID
@app.route("/players/<string:player_id>", methods=["DELETE"])
def delete_player(player_id):
    result = collection.delete_one({"_id": ObjectId(player_id)})
    
    if result.deleted_count == 0:
        return jsonify({"error": "Player not found"}), 404
    return jsonify({"message": "Player deleted successfully"})

if __name__ == "__main__":
    app.run(debug=True)