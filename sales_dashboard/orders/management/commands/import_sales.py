# sales/management/commands/import_sales.py
import csv
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from orders.models import Segment, Customer, ProductGroup, Product, Order, OrderItem
from dateutil import parser as date_parser
import pytz

# ===== Helpers =====
VIETNAM_TZ = pytz.timezone("Asia/Ho_Chi_Minh")

def safe_str(val):
    """Xử lý None, khoảng trắng và BOM"""
    return (val or "").strip().lstrip("\ufeff")

def safe_int(val, default=0):
    try:
        return int(safe_str(val))
    except (ValueError, TypeError):
        return default

def safe_decimal(val, default=Decimal("0")):
    try:
        return Decimal(safe_str(val).replace(",", ""))
    except (InvalidOperation, AttributeError):
        return default

def safe_datetime(val):
    """Chuyển string CSV thành timezone-aware datetime theo Asia/Ho_Chi_Minh"""
    if not val:
        return None
    try:
        val_str = safe_str(val)
        dt = date_parser.parse(val_str)
        if timezone.is_naive(dt):
            dt = VIETNAM_TZ.localize(dt)
        return dt
    except Exception as e:
        print(f"Warning: cannot parse datetime '{val}' -> {e}")
        return None

# ===== Command =====
class Command(BaseCommand):
    help = "Import orders from CSV/TSV file. Usage: python manage.py import_sales path/to/file.csv"

    def add_arguments(self, parser):
        parser.add_argument("csvfile", type=str)

    def handle(self, *args, **options):
        path = options["csvfile"]

        with open(path, newline="", encoding="utf-8") as f:
            # Detect delimiter
            first_line = f.readline()
            if ";" in first_line:
                delimiter = ";"
            elif "\t" in first_line:
                delimiter = "\t"
            else:
                delimiter = ","
            f.seek(0)

            reader = csv.DictReader(f, delimiter=delimiter)
            order_items = []
            count = 0

            with transaction.atomic():
                for row in reader:
                    # ===== Parse dữ liệu =====
                    # Xử lý BOM trong tên cột
                    raw_date = (row.get("Thời gian tạo đơn") or 
                               row.get("\ufeffThời gian tạo đơn") or 
                               row.get("Thoi gian tao don"))
                    created_at = safe_datetime(raw_date)
                    order_code = safe_str(row.get("Mã đơn hàng") or row.get("Ma don hang"))
                    customer_code = safe_str(row.get("Mã khách hàng") or row.get("Ma khach hang"))
                    customer_name = safe_str(row.get("Tên khách hàng") or row.get("Ten khach hang"))
                    segment_code = safe_str(row.get("Mã PKKH") or row.get("Ma PKKH"))
                    segment_desc = safe_str(row.get("Mô tả Phân Khúc Khách hàng") or row.get("Mo ta Phan Khuc"))

                    group_code = safe_str(row.get("Mã nhóm hàng") or row.get("Ma nhom hang"))
                    group_name = safe_str(row.get("Tên nhóm hàng") or row.get("Ten nhom hang"))
                    product_code = safe_str(row.get("Mã mặt hàng") or row.get("Ma mat hang"))
                    product_name = safe_str(row.get("Tên mặt hàng") or row.get("Ten mat hang"))

                    cost_price = safe_decimal(row.get("Giá Nhập") or row.get("Gia Nhap"))
                    qty = safe_int(row.get("SL") or row.get("So luong"), default=1)
                    unit_price = safe_decimal(row.get("Đơn giá") or row.get("Don gia"))
                    line_total = safe_decimal(row.get("Thành tiền") or row.get("Thanh tien"), default=unit_price * qty)

                    # ===== Related objects =====
                    segment, _ = Segment.objects.get_or_create(
                        code=segment_code or "UNK",
                        defaults={"description": segment_desc},
                    )

                    customer, _ = Customer.objects.get_or_create(
                        code=customer_code or "UNK",
                        defaults={"name": customer_name, "segment": segment},
                    )
                    if customer.segment_id != segment.id:
                        customer.segment = segment
                        customer.save(update_fields=["segment"])

                    group, _ = ProductGroup.objects.get_or_create(
                        code=group_code or "UNK",
                        defaults={"name": group_name},
                    )

                    product, _ = Product.objects.get_or_create(
                        code=product_code or "UNK",
                        defaults={"name": product_name, "group": group, "cost_price": cost_price},
                    )
                    if cost_price and (not product.cost_price or product.cost_price == 0):
                        product.cost_price = cost_price
                        product.group = group
                        product.save(update_fields=["cost_price", "group"])

                    # ===== Order (update_or_create) =====
                    order, _ = Order.objects.update_or_create(
                        order_code=order_code or "UNK",
                        defaults={
                            "created_at": created_at or timezone.now(),
                            "customer": customer,
                        }
                    )

                    # ===== Gom OrderItem để bulk insert =====
                    order_items.append(
                        OrderItem(
                            order=order,
                            product=product,
                            quantity=qty,
                            unit_price=unit_price,
                            line_total=line_total,
                        )
                    )
                    count += 1

                # Bulk insert OrderItems theo batch
                OrderItem.objects.bulk_create(order_items, batch_size=1000, ignore_conflicts=True)

            self.stdout.write(self.style.SUCCESS(f"Imported {count} order items (bulk insert, batch_size=1000)"))
