from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId

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

# API Endpoints
@app.route("/players", methods=["GET"])
def get_players():
    players = list(collection.find())
    return jsonify([format_document(player) for player in players])

@app.route("/players", methods=["POST"])
def add_player():
    data = request.json
    result = collection.insert_one(data)
    return jsonify({"message": "Player added", "id": str(result.inserted_id)}), 201

@app.route("/players/<string:player_id>", methods=["DELETE"])
def delete_player(player_id):
    result = collection.delete_one({"_id": ObjectId(player_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Player not found"}), 404
    return jsonify({"message": "Player deleted successfully"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
