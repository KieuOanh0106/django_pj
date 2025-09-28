from django.db import models

# Create your models here.
# sales/models.py
from django.db import models
from decimal import Decimal

class Segment(models.Model):
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.code} - {self.description[:30]}"

class Customer(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    segment = models.ForeignKey(Segment, on_delete=models.PROTECT, related_name='customers')

    def __str__(self):
        return f"{self.code} - {self.name}"

class ProductGroup(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Product(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    group = models.ForeignKey(ProductGroup, on_delete=models.PROTECT, related_name='products')
    cost_price = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    order_code = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField()
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='orders')

    def __str__(self):
        return self.order_code

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=14, decimal_places=2)
    line_total = models.DecimalField(max_digits=16, decimal_places=2)

    def __str__(self):
        return f"{self.order.order_code} - {self.product.code}"

