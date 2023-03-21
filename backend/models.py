from django.db import models
from django.contrib import admin

class User(models.Model):
    id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    password = models.CharField(max_length=50)
    account_number = models.IntegerField()
    phone_number = models.IntegerField()
    country = models.CharField(max_length=50)
    def __str__(self):
        return self.first_name + " " + self.last_name

class Category(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    parent_id = models.ForeignKey(to='self',null=True,on_delete=models.CASCADE)
    def __str__(self):
        return self.name

class Budget(models.Model):
    id = models.CharField(primary_key=True,max_length=50)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2,max_digits=10)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.CharField(max_length=100)
    date = models.DateTimeField()
    def __str__(self):
        return self.description

# class Expense(models.Model):
#     id = models.CharField(primary_key=True)
#     user_id = models.ForeignKey(User, on_delete=models.CASCADE)
#     amount = models.DecimalField(decimal_places=2)
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)
#     description = models.CharField(max_length=100)
#     date = models.DateField()

    # def __str__(self):
    #     return self.description