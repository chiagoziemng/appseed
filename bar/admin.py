# bar/admin.py
from django.contrib import admin
from .models import Category, Drink, Order, Transaction, Invoice

# bar/admin.py
@admin.register(Drink)
class DrinkAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'quantity_in_stock')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('drink', 'quantity', 'total_price')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_date', 'total_amount')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'invoice_date')


admin.site.register(Category)

