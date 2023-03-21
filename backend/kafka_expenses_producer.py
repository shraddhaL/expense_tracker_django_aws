import json
from kafka import KafkaProducer
import os

KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS')

EXPENSE_TOPIC = 'expense_data'

# Set up the Kafka producer configuration
producer_config = {
    'bootstrap_servers': KAFKA_BOOTSTRAP_SERVERS,  # list of Kafka broker addresses
    # Additional configuration options can be added here
    'value_serializer':lambda v: json.dumps(v).encode('utf-8')
}

# Instantiate the Kafka producer
producer = KafkaProducer(**producer_config)

def send_expense_data_to_kafka(event_type, user_id, expense_amount,expense_category,expense_date):
    event_data = {
        'event_type': event_type,
        'user_id': user_id,
        'expense_amount': expense_amount,
        'expense_category': expense_category,
        'expense_date': expense_date
    }
    producer.send(EXPENSE_TOPIC, value=event_data)
