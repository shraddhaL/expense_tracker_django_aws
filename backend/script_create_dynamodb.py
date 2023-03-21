import boto3
from botocore.exceptions import ClientError

# Create a DynamoDB client
dynamodb = boto3.client('dynamodb')

# Define the table name and key schema
table_name = 'expenses'
key_schema = [
    {
        'AttributeName': 'id',
        'KeyType': 'HASH'
    }
]

# Define the attribute definitions and table provisioned throughput
attribute_definitions = [
    {
        'AttributeName': 'id',
        'AttributeType': 'N'
    }
]

provisioned_throughput = {
    'ReadCapacityUnits': 5,
    'WriteCapacityUnits': 5
}

# Create the table if it doesn't already exist
try:
    response = dynamodb.create_table(
        TableName=table_name,
        KeySchema=key_schema,
        AttributeDefinitions=attribute_definitions,
        ProvisionedThroughput=provisioned_throughput
    )
    print(f"Table '{table_name}' created.")
except ClientError as e:
    if e.response['Error']['Code'] == 'ResourceInUseException':
        print(f"Table '{table_name}' already exists.")
    else:
        print(f"Unexpected error: {e}")