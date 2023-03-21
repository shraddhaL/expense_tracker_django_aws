# from django.shortcuts import render
from decimal import Decimal
import decimal
import hashlib
from rest_framework.response import Response
from rest_framework.decorators import api_view

from backend.kafka_expenses_producer import send_expense_data_to_kafka
from .models import Budget, User, Category
from .serializer import BudgetSerializer, UserSerializer,CategorySerializer
from rest_framework import status
from django.shortcuts import get_object_or_404
import json
from django.http import JsonResponse
from .query_dynamodb import get_dynamodb_resource
import redis
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
import ast,yaml,pickle
import pickle

# Create your views here.
@api_view(['GET'])
def getUser(request):
    user = User.objects.all()
    serializer = UserSerializer(user, many=True)
    return Response(serializer.data)

#create a class for get menthod for user
# class UserList(APIView):
#     def get(self, request):
#         queryset = User.objects.all()
#         serializer_class = UserSerializer(queryset, many=True)
#         return Response(serializer_class.data)

@api_view(['POST'])
def postUser(request):
    serializer = UserSerializer(data=request.data)
 
    if serializer.is_valid():
        serializer.save()
        return Response({"status": "success", "data": serializer.data}, status=200)
    return Response({"status": "error", "data": serializer.errors}, status=400)

@api_view(['PUT'])
def updateUser(request,pk):
    item = User.objects.get(pk=pk)
    data = UserSerializer(instance=item, data=request.data)
    if data.is_valid():
        data.save()
        return Response(data.data)
    else:
        return Response({"status": "error", "data": data.errors}, status=400)

@api_view(['DELETE'])
def deleteUser(request,pk):
    item = get_object_or_404(User, pk=pk)
    item.delete()
    return Response(status=status.HTTP_202_ACCEPTED)

#Model for Category

@api_view(['GET'])
def getCategory(request):
    category = Category.objects.all()
    serializer = CategorySerializer(category, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def postCategory(request):
    serializer = CategorySerializer(data=request.data)
 
    if serializer.is_valid():
        serializer.save()
        return Response({"status": "success", "data": serializer.data}, status=200)
    return Response({"status": "error", "data": serializer.errors}, status=400)

@api_view(['PUT'])
def updateCategory(request,pk):
    item = Category.objects.get(pk=pk)
    data = CategorySerializer(instance=item, data=request.data)
    if data.is_valid():
        data.save()
        return Response(data.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def deleteCategory(request, pk):
    item = get_object_or_404(Category, pk=pk)
    item.delete()
    return Response(status=status.HTTP_202_ACCEPTED)

#Model for Budget

@api_view(['GET'])
def getBudget(request):
    budget = Budget.objects.all()
    serializer = BudgetSerializer(budget, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def postBudget(request):
    serializer = BudgetSerializer(data=request.data)
 
    if serializer.is_valid():
        serializer.save()
        return Response({"status": "success", "data": serializer.data}, status=200)
    return Response({"status": "error", "data": serializer.errors}, status=400)

@api_view(['PUT'])
def updateBudget(request,pk):
    item = Budget.objects.get(pk=pk)
    data = BudgetSerializer(instance=item, data=request.data)
    if data.is_valid():
        data.save()
        return Response(data.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def deleteBudget(request, pk):
    item = get_object_or_404(Budget, pk=pk)
    item.delete()
    return Response(status=status.HTTP_202_ACCEPTED)


redis_client = redis.Redis(host='ec2-18-206-208-125.compute-1.amazonaws.com', port=6379)

    # if redis_client.exists(arg):
    #     return redis_client.get(arg)
    # else:
    #     # Expensive computation
    #     result = ...
    #     redis_client.set(arg, result)
    #     return result

#class MyEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, Decimal):
#             return str(obj)
#         return super().default(obj)
# def custom_decoder(obj):
#     if isinstance(obj, str):
#         try:
#             return Decimal(obj)
#         except:
#             pass
#     return obj
# 
# i have used pickle to serialize and deserialize the data, 
# but you can use json as it is more popular and secure.
#
#To use, replace the pickle.dumps and pickle.loads with json.dumps and json.loads.
#Use json.dumps(my_object, cls=MyEncoder) and json.loads(json_string, object_hook=custom_decoder)
# 
#

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

class DecimalDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(parse_float=Decimal, *args, **kwargs)

    def decode(self, *args, **kwargs):
        obj = super().decode(*args, **kwargs)
        return self._parse_object(obj)

    def _parse_object(self, obj):
        if isinstance(obj, list):
            return [self._parse_object(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: self._parse_object(value) for key, value in obj.items()}
        elif isinstance(obj, int):
            return Decimal(obj)
        return obj

# Dynamodb Expense Endpoint
@api_view(['POST'])
def postExpense(request):
    dynamodb = get_dynamodb_resource()
    table = dynamodb.Table('expenses')

    # Parse the JSON request body
    body = json.loads(request.body)

    # Construct the item to be written to the table
    item = {
        'id': body['id'],
        'user_id': body['user_id'],
        'amount': body['amount'],
        'category': body['category'],
        'description': body['description'],
        'date': body['date']
    }
    # my_object = {
    #     'id': int(body['id']),
    #     'user_id': int(body['user_id']),
    #     'amount': Decimal(body['amount']),
    #     'category': int(body['category']),
    #     'description': str(body['description']),
    #     'date': str(body['date'])
    # }
    # Write the item to the table
    response = table.put_item(Item=item)
    
    # Return a JSON response indicating success or failure
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        #set expense data to redis
        redis_client.set(f"expenses:{body['id']}",json.dumps(item))
        
        #send_expense_data_to_kafka
        send_expense_data_to_kafka("add",item['user_id'], item['amount'], item['category'], item['date'])

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})
    
@api_view(['PUT'])
def updateExpense(request,pk):
    dynamodb = get_dynamodb_resource()
    table = dynamodb.Table('expenses')

    # Parse the JSON request body
    body = json.loads(request.body)

    # Construct the item to be written to the table
    response = table.update_item(
        Key={
                'id': pk,
            },
            UpdateExpression='SET amount = :amount_value',
            ExpressionAttributeValues={
                ':amount_value': body['amount']
            }
        )

    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        if redis_client.exists(f"expenses:{pk}"):
            try:
                result = redis_client.get(f"expenses:{pk}")
                result = json.loads(result)
                result['amount'] = body['amount']
                redis_client.set(f"expenses:{pk}",json.dumps(result))
            except json.JSONDecodeError:
                # Handle unpickling error
                result = {}
                redis_client.delete(f"expenses:{pk}")
            
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})

@api_view(['GET'])
def getExpense(request, pk):
    dynamodb = get_dynamodb_resource()
    table = dynamodb.Table('expenses')
    if redis_client.exists(f"expenses:{pk}"):
        result_str = redis_client.get(f"expenses:{pk}")
        try:
            result = json.loads(result_str)
            print(result)
            print(type(result))
        except json.JSONDecodeError:
            result = {}
            redis_client.delete(f"expenses:{pk}")
        print("cache hit")
    else:
        response = table.get_item(
            Key = {
                'id': pk
            }
        )
        result = response.get('Item', {})
        result_str = json.dumps(result, cls=DecimalEncoder)
        redis_client.set(f"expenses:{pk}", result_str)
        print("cache miss")

    return Response({"status": "success", "data": result}, status=200)

@api_view(['DELETE'])
def deleteExpense(request, pk):
    dynamodb = get_dynamodb_resource()
    table = dynamodb.Table('expenses')
    response = table.delete_item(
        Key = {
                'id': pk
               }
        )
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        if redis_client.exists(f"expenses:{pk}"):
            redis_client.delete(f"expenses:{pk}")
        return JsonResponse({'status': 'deleted'})
    else:
        return JsonResponse({'status': 'error'})

# @api_view(['POST'])
# def postExpense(request):
#     dynamodb = get_dynamodb_resource()
#     table = dynamodb.Table('expenses')

#     # Parse the JSON request body
#     body = json.loads(request.body)

#     # Construct the item to be written to the table
#     item = {
#         'id': body['id'],
#         'user_id': body['user_id'],
#         'amount': body['amount'],
#         'category': body['category'],
#         'description': body['description'],
#         'date': body['date']
#     }
#     my_object = {
#         'id': int(body['id']),
#         'user_id': int(body['user_id']),
#         'amount': Decimal(body['amount']),
#         'category': int(body['category']),
#         'description': str(body['description']),
#         'date': str(body['date'])
#     }
#     # Write the item to the table
#     response = table.put_item(Item=item)
    
#     # Return a JSON response indicating success or failure
#     if response['ResponseMetadata']['HTTPStatusCode'] == 200:
#         redis_client.set(body['id'],pickle.dumps(my_object))
#         return JsonResponse({'status': 'success'})
#     else:
#         return JsonResponse({'status': 'error'})
    
# @api_view(['PUT'])
# def updateExpense(request,pk):
#     dynamodb = get_dynamodb_resource()
#     table = dynamodb.Table('expenses')

#     # Parse the JSON request body
#     body = json.loads(request.body)

#     # Construct the item to be written to the table
#     response = table.update_item(
#         Key={
#                 'id': pk,
#             },
#             UpdateExpression='SET amount = :amount_value',
#             ExpressionAttributeValues={
#                 ':amount_value': body['amount']
#             }
#         )

#     if response['ResponseMetadata']['HTTPStatusCode'] == 200:
#         if redis_client.exists(pk):
#             try:
#                 result = redis_client.get(pk)
#                 result = pickle.loads(result)
#                 result['amount'] = decimal.Decimal(body['amount'])
#                 redis_client.set(pk,pickle.dumps(result))
#             except pickle.UnpicklingError:
#                 # Handle unpickling error
#                 result = {}
#                 redis_client.delete(pk)
            
#         return JsonResponse({'status': 'success'})
#     else:
#         return JsonResponse({'status': 'error'})

# @api_view(['GET'])
# def getExpense(request, pk):
#     dynamodb = get_dynamodb_resource()
#     table = dynamodb.Table('expenses')
#     if redis_client.exists(pk):
#         result_str = redis_client.get(pk)
#         try:
#             result = pickle.loads(result_str)
#             print(result)
#         except pickle.UnpicklingError:
#             # Handle unpickling error
#             result = {}
#             redis_client.delete(pk)
#         print("cache hit")
#     else:
#         response = table.get_item(
#             Key = {
#                 'id': pk
#             }
#         )
#         result = response.get('Item', {})
#         result_str = pickle.dumps(result)
#         print(result_str)
#         print(type(result_str))
#         redis_client.set(pk, result_str)
#         print("cache miss")

#     return Response({"status": "success", "data": result}, status=200)


# @api_view(['DELETE'])
# def deleteExpense(request, pk):
#     dynamodb = get_dynamodb_resource()
#     table = dynamodb.Table('expenses')
#     response = table.delete_item(
#         Key = {
#                 'id': pk
#                }
#         )
#     if response['ResponseMetadata']['HTTPStatusCode'] == 200:
#         if redis_client.exists(pk):
#             redis_client.delete(pk)
#         return JsonResponse({'status': 'deleted'})
#     else:
#         return JsonResponse({'status': 'error'})
