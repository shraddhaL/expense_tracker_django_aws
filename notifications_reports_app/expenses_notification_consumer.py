import json
import os
from kafka import KafkaConsumer
from django.core.mail import send_mail

KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS')
#KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']
EXPENSE_TOPIC = 'expense_data'

# Set up the Kafka consumer configuration
consumer_config = {
    'bootstrap_servers': KAFKA_BOOTSTRAP_SERVERS,  # list of Kafka broker addresses
    'auto_offset_reset': 'earliest',  # start consuming from the beginning of the topic
    'value_deserializer': lambda m: json.loads(m.decode('ascii')),  # deserialize messages as JSON
    'group_id':'email-service-group',
    # Additional configuration options can be added here
}

# Instantiate the Kafka consumer
consumer = KafkaConsumer(EXPENSE_TOPIC, **consumer_config)

for message in consumer:
    event_data = message.value
    event_type = event_data.get('event_type')
    user_id = event_data.get('user_id')
    amount = event_data.get('expense_amount')   
    category = event_data.get('expense_category')   
    date = event_data.get('expense_date')    

    if event_type == 'add':
        # Perform some action, such as sending an email notification
        # send_mail(
        #     'New expense added',
        #     f'You added a new expense of {amount}',
        #     'noreply@example.com',
        #     ['user@example.com'],
        #     fail_silently=False,
        # )
        print(f'Expense {amount} for user {user_id} was added in category {category} on {date}')
    elif event_type == 'update':
        # Perform some action, such as logging the expense event
        print(f'Expense for user {user_id}was updated to {amount} in category {category} on {date}')
    elif event_type == 'delete':
        # Perform some action, such as logging the expense event
        print(f'Expense for user {user_id} was deleted in category {category} on {date}')
