import random
import datetime
import time
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['flight_status_db']
collection = db['flights']

# Define possible status updates and gates
statuses = ["On-Time", "Delayed", "Cancelled"]
gates = [str(i) for i in range(1, 51)]

# List of flight numbers to monitor and update
flight_numbers_to_monitor = ["6E4523", "6E7155", "6E1234"]  # Add the flight numbers you want to track

def update_flight_data():
    # Fetch flights that match the specified flight numbers
    flights = list(collection.find({'flight_number': {'$in': flight_numbers_to_monitor}}))

    if not flights:
        print("No matching flights found in the database.")
        return

    # Randomly select a flight to update
    flight_to_update = random.choice(flights)

    # Generate new data for the selected flight
    new_status = random.choice(statuses)
    new_gate = random.choice(gates)
    new_departure_time = datetime.datetime.now() + datetime.timedelta(minutes=random.randint(10, 120))

    # Update the flight in the database
    collection.update_one(
        {'_id': flight_to_update['_id']},
        {
            '$set': {
                'status': new_status,
                'gate': new_gate,
                'departure_time': new_departure_time.isoformat()
            }
        }
    )

    # Print the updated information for the flight
    print(f"Updated flight {flight_to_update['flight_number']} with new status: {new_status}, gate: {new_gate}, departure time: {new_departure_time}")

if __name__ == "__main__":
    while True:
        update_flight_data()
        # Sleep for a certain period before the next update
        time.sleep(10)  # Update every minute
