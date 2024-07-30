from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson import json_util
import json
from datetime import datetime
from config import MONGO_URI
from kafka import KafkaProducer
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Kafka Producer configuration
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client.get_database()  # This will use 'flight_status_db' as specified in MONGO_URI
flights_collection = db.flights

def serialize_flight(flight):
    # Convert ObjectId to string
    flight['_id'] = str(flight['_id'])
    return flight

def notify_clients():
    flights = list(flights_collection.find())
    serialized_flights = [serialize_flight(flight) for flight in flights]
    print(f"Notifying Kafka with the following data: {serialized_flights}")
    producer.send('database_updates', serialized_flights)
    producer.flush()  # Ensure all messages are sent
    print(f"Emitted flight data to Kafka: {serialized_flights}")


# Route to search flights
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
        date_str = departure_date_start.date().isoformat()

        # Find flights based on search criteria
        if flight_number:
            flights = flights_collection.find({'flight_number': flight_number})
        else:
            flights = flights_collection.find({
                'departure_airport': departure_airport,
                'arrival_airport': arrival_airport,
                'departure_date': date_str
            })

        flight_list = list(flights)
        print(f"Flights found: {flight_list}")

        if not flight_list:
            return jsonify({'message': 'No flights found'}), 404

        # Notify Kafka about new flight data
        notify_clients()
        
        # Return the flights as JSON
        return json_util.dumps(flight_list), 200

    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

if __name__ == '__main__':
    app.run(debug=True)
