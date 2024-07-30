from pymongo import MongoClient
from kafka import KafkaProducer
import json

# MongoDB setup
client = MongoClient('mongodb://localhost:27017')
db = client['flight_status_db']
flights_collection = db['flights']

# Kafka setup
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def process_change(change):
    print("Received change:", change)  # Print the change object for debugging

    # Determine the type of operation and extract the relevant data
    if change['operationType'] == 'insert':
        flight = change['fullDocument']
    elif change['operationType'] == 'update':
        # Check if 'fullDocument' is present, otherwise handle 'updateDescription'
        if 'fullDocument' in change:
            flight = change['fullDocument']
        else:
            print("Update event missing 'fullDocument'. Using 'updateDescription'.")
            updated_fields = change['updateDescription']['updatedFields']
            # Construct a flight object with updated fields, assuming you have some defaults
            flight = {
                'flight_number': updated_fields.get('flight_number', 'Unknown'),
                'status': updated_fields.get('status', 'Unknown'),
                'gate': updated_fields.get('gate', 'Unknown'),
                'terminal': updated_fields.get('terminal', 'Unknown'),
                'departure_time': updated_fields.get('departure_time', 'Unknown'),
                'arrival_time': updated_fields.get('arrival_time', 'Unknown')
            }
    elif change['operationType'] == 'replace':
        flight = change['fullDocument']
    else:
        print("Unhandled operationType:", change['operationType'])
        return

    # Construct the message to send to Kafka
    message = {
        'flight_number': flight['flight_number'],
        'status': flight['status'],
        'gate': flight['gate'],
        'terminal': flight['terminal'],
        'departure_time': flight['departure_time'],
        'arrival_time': flight['arrival_time']
    }
    
    # Send the message to Kafka
    producer.send('flight_updates', message)
    producer.flush()

# Create the change stream with fullDocument option for update events
change_stream = flights_collection.watch(full_document='updateLookup')

# Listen to changes in the flights collection and process them
for change in change_stream:
    process_change(change)
