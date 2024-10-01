from django.contrib import admin 
from .models import Product, Cart, Order, OrderItem, updateStockRequest,Category,Supplier

# Register your models here.

admin.site.register(updateStockRequest)
admin.site.register(Category)
admin.site.register(Supplier)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['fullname', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['fullname', 'address', 'postal_code']
