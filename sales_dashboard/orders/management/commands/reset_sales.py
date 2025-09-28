from django.core.management.base import BaseCommand
from orders.models import OrderItem, Order, Product, ProductGroup, Customer, Segment

class Command(BaseCommand):
    help = "Xóa toàn bộ dữ liệu sales (OrderItem, Order, Product, ProductGroup, Customer, Segment)"

    def handle(self, *args, **kwargs):
        # Xoá theo thứ tự phụ thuộc
        self.stdout.write("Đang xóa dữ liệu...")

        OrderItem.objects.all().delete()
        self.stdout.write("✅ Đã xoá OrderItem")

        Order.objects.all().delete()
        self.stdout.write("✅ Đã xoá Order")

        Product.objects.all().delete()
        self.stdout.write("✅ Đã xoá Product")

        ProductGroup.objects.all().delete()
        self.stdout.write("✅ Đã xoá ProductGroup")

        Customer.objects.all().delete()
        self.stdout.write("✅ Đã xoá Customer")

        Segment.objects.all().delete()
        self.stdout.write("✅ Đã xoá Segment")

        self.stdout.write(self.style.SUCCESS("🎉 Toàn bộ dữ liệu sales đã được xoá thành công!"))
