from rest_framework import serializers
from .models import User,Category,Budget

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=('__all__')

# serializer for category
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields=('__all__')

# serializer for budget
class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model=Budget
        fields=('__all__')