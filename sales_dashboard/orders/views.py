from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from orders.models import OrderItem, Order, Customer, Product, ProductGroup, Segment
import logging

logger = logging.getLogger(__name__)

def dashboard(request):
    """Dashboard view với các biểu đồ D3.js"""
    logger.info(f"Dashboard accessed from {request.META.get('HTTP_HOST', 'unknown')}")
    return render(request, 'sales/index.html')

@csrf_exempt
@require_http_methods(["GET"])
def api_sales_data(request):
    """API endpoint để cung cấp dữ liệu bán hàng cho frontend"""
    logger.info(f"API sales data requested from {request.META.get('HTTP_HOST', 'unknown')}")
    qs = OrderItem.objects.select_related('order','product__group','order__customer__segment').all()
    data = []
    for item in qs:
        data.append({
            'Mã đơn hàng': item.order.order_code,
            'Thời gian tạo đơn': item.order.created_at.strftime('%Y-%m-%d %H:%M:%S') if item.order.created_at else '',
            'Mã khách hàng': item.order.customer.code,
            'Tên khách hàng': item.order.customer.name,
            'Mã PKKH': item.order.customer.segment.code,
            'Mô tả Phân Khúc Khách hàng': item.order.customer.segment.description,
            'Mã nhóm hàng': item.product.group.code,
            'Tên nhóm hàng': item.product.group.name,
            'Mã mặt hàng': item.product.code,
            'Tên mặt hàng': item.product.name,
            'Giá Nhập': float(item.product.cost_price) if item.product.cost_price else 0,
            'SL': item.quantity,
            'Đơn giá': float(item.unit_price),
            'Thành tiền': float(item.line_total),
        })
    
    logger.info(f"Returning {len(data)} records to {request.META.get('HTTP_HOST', 'unknown')}")
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})

@csrf_exempt
@require_http_methods(["GET"])
def api_test(request):
    """API test đơn giản để kiểm tra kết nối"""
    logger.info(f"API test requested from {request.META.get('HTTP_HOST', 'unknown')}")
    return JsonResponse({
        'status': 'success',
        'message': 'API hoạt động bình thường!',
        'data': {
            'total_orders': Order.objects.count(),
            'total_customers': Customer.objects.count(),
            'total_products': Product.objects.count(),
            'total_segments': Segment.objects.count(),
            'total_product_groups': ProductGroup.objects.count(),
            'total_order_items': OrderItem.objects.count()
        }
    }, json_dumps_params={'ensure_ascii': False})
