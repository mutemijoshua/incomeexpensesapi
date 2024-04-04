from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from .serializers import ExpensesSerializer
from .models import Expense
from rest_framework import permissions
from .permissions import IsOwner



class ExpenseListAPIView(ListCreateAPIView):
    serializer_class=ExpensesSerializer
    queryset = Expense.objects.all()
    permissions_classes =(permissions.IsAuthenticated)
    #override the method that creates an instance of an expense
    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)
        
    #define a queerry set for getting objects

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)
    
class ExpenseDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class=ExpensesSerializer
    queryset = Expense.objects.all()
    permissions_classes =(permissions.IsAuthenticated, IsOwner,)
    lookup_field= "id"
   
    #define a queerry set for getting objects
    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)