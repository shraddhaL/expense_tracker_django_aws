from django.urls import path
from . import views
from django.conf import settings

urlpatterns = [
    path('users', views.getUser),
    path('user/post/', views.postUser),
    path('user/edit/<int:pk>/', views.updateUser),
    path('user/delete/<int:pk>/', views.deleteUser),
    path('category', views.getCategory),
    path('category/post/', views.postCategory),
    path('category/edit/<int:pk>/', views.updateCategory),
    path('category/delete/<int:pk>/', views.deleteCategory),
    path('budget', views.getBudget),
    path('budget/post/', views.postBudget),
    path('budget/edit/<int:pk>/', views.updateBudget),
    path('budget/delete/<int:pk>/', views.deleteBudget),
    path('expenses', views.postExpense),
    path('expenses/edit/<int:pk>/', views.updateExpense),
    path('expenses/<int:pk>/', views.getExpense),
    path('expenses/delete/<int:pk>/', views.deleteExpense)


]