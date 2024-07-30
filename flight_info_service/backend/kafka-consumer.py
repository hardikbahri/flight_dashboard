from flask import Flask, Response
from kafka import KafkaConsumer
import json



# Kafka Consumer configuration
consumer = KafkaConsumer(
    'database_updates',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)




for message in consumer:
    database_update = message.value
    print(f"Received message: {database_update}")


