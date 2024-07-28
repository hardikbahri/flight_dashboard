from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson import json_util
import json
from datetime import datetime
from config import MONGO_URI
from flask_cors import CORS

app = Flask(__name__)
# In your app.py


CORS(app)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
# MongoDB connection
client = MongoClient(MONGO_URI)
db = client.get_database()  # This will use 'flight_status_db' as specified in MONGO_URI
flights_collection = db.flights

# Route to get flight information by flight number
@app.route('/flights/<string:flight_number>', methods=['GET'])
def get_flight_info(flight_number):
    flight = flights_collection.find_one({'flight_number': flight_number})
    if flight:
        return json_util.dumps(flight), 200  # Use json_util.dumps for BSON objects
    else:
        return jsonify({'error': 'Flight not found'}), 404

# Route to get all flights
@app.route('/flights', methods=['GET'])
def get_all_flights():
    flights = list(flights_collection.find())
    return json_util.dumps(flights), 200  # Use json_util.dumps for BSON objects

# Route to add a new flight
@app.route('/flights', methods=['POST'])
def add_flight():
    new_flight = request.json
    flight_id = flights_collection.insert_one(new_flight).inserted_id
    return jsonify(str(flight_id)), 201

# Route to update a flight's status
@app.route('/search-flights', methods=['POST'])
def search_flights():
    payload = request.get_json()
    if not payload:
        return jsonify({'error': 'Invalid input'}), 400

    departure_airport = payload.get('departing')
    arrival_airport = payload.get('arriving')
    departure_date = payload.get('date')
    flight_number = payload.get('flightNumber') if payload.get('flightNumber') else None

    # Check if any of the required fields are missing
    if not departure_airport or not arrival_airport or not departure_date:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        # Parse the input date
        departure_date_start = datetime.fromisoformat(departure_date)

        # Create the date string in the format yyyy-mm-dd to match only the date part
        date_str = departure_date_start.date().isoformat()

        # Find flights based on search criteria
        if flight_number:
            flights = flights_collection.find({
                'flight_number': flight_number
            })
        else:
            flights = flights_collection.find({
                'departure_airport': departure_airport,
                'arrival_airport': arrival_airport,
                'departure_date': date_str
            })

        # Convert the cursor to a list
        flight_list = list(flights)
        print("Flights found:", flight_list)

        if not flight_list:
            return jsonify({'message': 'No flights found'}), 404

        # Return the flights as JSON
        return json_util.dumps(flight_list), 200

    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    

# Route to delete a flight
@app.route('/flights/<string:flight_number>', methods=['DELETE'])
def delete_flight(flight_number):
    result = flights_collection.delete_one({'flight_number': flight_number})
    if result.deleted_count > 0:
        return jsonify({'message': 'Flight deleted'}), 200
    else:
        return jsonify({'error': 'Flight not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
