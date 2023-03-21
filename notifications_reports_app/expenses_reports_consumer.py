import json
import pandas as pd
from kafka import KafkaConsumer
from django.core.mail import send_mail

KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']
EXPENSE_TOPIC = 'expense_data'

# Set up the Kafka consumer configuration
consumer_config = {
    'bootstrap_servers': KAFKA_BOOTSTRAP_SERVERS,  # list of Kafka broker addresses
    'auto_offset_reset': 'earliest',  # start consuming from the beginning of the topic
    'value_deserializer': lambda m: json.loads(m.decode('ascii')),  # deserialize messages as JSON
    'group_id':'report-service-group',
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
    
    
    if event_type == 'add' or event_type == 'update' or event_type == 'delete':
        df = pd.DataFrame([event_data]) 
        print(df.describe())
        
        category_totals = df.groupby('category')['amount'].sum()
        print(category_totals)