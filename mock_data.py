import random
import datetime
from pymongo import MongoClient

# Generate mock flight data with unique departure and arrival airports
def generate_mock_flight_data(num_records):
    flight_data = []
    airlines = ["Indigo"]
    airports = ["DEL", "BOM", "HYD", "BLR", "MAA"]
    statuses = ["On-Time", "Delayed", "Cancelled"]

    for _ in range(num_records):
        flight_number = f"6E{random.randint(100, 9999)}"
        departure_airport = random.choice(airports)
        # Ensure arrival airport is different from departure airport
        available_airports = [airport for airport in airports if airport != departure_airport]
        arrival_airport = random.choice(available_airports)
        departure_time = datetime.datetime.now() + datetime.timedelta(hours=random.randint(1, 12))
        arrival_time = departure_time + datetime.timedelta(hours=random.randint(2, 6))
        status = random.choice(statuses)
        gate = f"{random.randint(1, 50)}"
        terminal = f"{random.randint(1, 5)}"
        airline = random.choice(airlines)
        departure_date = departure_time.date().isoformat()
        arrival_date = arrival_time.date().isoformat()
        flight = {
            "flight_number": flight_number,
            "departure_airport": departure_airport,
            "arrival_airport": arrival_airport,
            "departure_time": departure_time.isoformat(),
            "arrival_time": arrival_time.isoformat(),
            "status": status,
            "gate": gate,
            "terminal": terminal,
            "airline": airline,
            "departure_date":departure_date,
            "arrival_date":arrival_date
            
        }

        flight_data.append(flight)

    return flight_data

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['flight_status_db']
collection = db['flights']

# Generate and insert mock data
mock_data = generate_mock_flight_data(100)
collection.insert_many(mock_data)

print(f"{len(mock_data)} flight records inserted into the 'flights' collection in the 'flight_status_db' database.")
