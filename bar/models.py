# bar/models.py
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Drink(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    quantity_in_stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    

class DrinkHistory(models.Model):
    drink = models.ForeignKey(Drink, on_delete=models.CASCADE)
    action = models.CharField(max_length=20)  # "ADD" or "REDUCE"
    quantity_changed = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} {self.quantity_changed} for {self.drink.name} at {self.timestamp}"

class Order(models.Model):
    drink = models.ForeignKey(Drink, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Allow null and blank

    def __str__(self):
        return f"{self.quantity} x {self.drink.name} - Total: {self.total_price}"

class Transaction(models.Model):
    transaction_date = models.DateTimeField(auto_now_add=True)
    orders = models.ManyToManyField(Order)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)

class Invoice(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE)
    invoice_date = models.DateTimeField(auto_now_add=True)
    # Add other fields for customer details if needed
