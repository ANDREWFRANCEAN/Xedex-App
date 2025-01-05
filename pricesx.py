from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import os

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Path to the JSON data file
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')


# Load data from JSON file
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    return []


# Save data to JSON file
def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)


# API to fetch all items
@app.route('/get_items', methods=['GET'])
def get_items():
    data = load_data()
    return jsonify(data)


# API to fetch the price of a specific item
@app.route('/get_price', methods=['GET'])
def get_price():
    item_name = request.args.get('item_name', '').strip().lower()
    data = load_data()

    # Search for the item in the list
    for item in data:
        if item['name'].strip().lower() == item_name:
            return jsonify({"item_name": item['name'], "price": item['price']})

    # If the item is not found
    return jsonify({"error": "Item not found"}), 404


# API to add or update an item
@app.route('/add_item', methods=['POST'])
def add_item():
    request_data = request.get_json()
    item_name = request_data.get('name', '').strip()
    price = request_data.get('price')

    if not item_name or price is None:
        return jsonify({"error": "Invalid input"}), 400

    data = load_data()

    # Check if item already exists
    for item in data:
        if item['name'].strip().lower() == item_name.strip().lower():
            item['price'] = price
            save_data(data)
            return jsonify({"message": f"Item '{item_name}' updated successfully"})

    # Add new item
    data.append({"name": item_name, "price": price})
    save_data(data)
    return jsonify({"message": f"Item '{item_name}' added successfully"})


# API to delete an item
@app.route('/delete_item', methods=['DELETE'])
def delete_item():
    request_data = request.get_json()
    item_name = request_data.get('name', '').strip().lower()

    if not item_name:
        return jsonify({"error": "Invalid input"}), 400

    data = load_data()
    for item in data:
        if item['name'].strip().lower() == item_name:
            data.remove(item)
            save_data(data)
            return jsonify({"message": f"Item '{item_name}' deleted successfully"})

    return jsonify({"error": "Item not found"}), 404


# Route to serve the HTML page
@app.route('/')
def home():
    return render_template('prices.html')

@app.route('/get_suggestions', methods=['GET'])
def get_suggestions():
    query = request.args.get('query', '').strip().lower()
    if not query:
        return jsonify([])  # Return empty list if no query

    data = load_data()
    suggestions = [item['name'] for item in data if query in item['name'].lower()]
    return jsonify(suggestions)

PASSKEY = "1234"

@app.route('/validate_passkey', methods=['POST'])
def validate_passkey():
    data = request.get_json()
    provided_passkey = data.get("passkey", "")

    if provided_passkey == PASSKEY:
        return jsonify({"success": True, "message": "Passkey validated."})
    else:
        return jsonify({"success": False, "message": "Invalid passkey."}), 403
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
