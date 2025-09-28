from django.contrib import admin

# Register your models here.
# sales/admin.py
from orders.models import Segment, Customer, ProductGroup, Product, Order, OrderItem

admin.site.register(Segment)
admin.site.register(Customer)
admin.site.register(ProductGroup)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)

