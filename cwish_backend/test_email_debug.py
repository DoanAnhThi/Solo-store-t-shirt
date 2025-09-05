#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwish_backend.settings')
django.setup()

from store.models import Order
from store.views import OrderViewSet

def test_email_debug():
    # Lấy order cuối cùng
    order = Order.objects.last()
    if not order:
        print("❌ No orders found")
        return

    print(f"🧪 Testing email for Order #{order.id}")

    # Tạo instance của OrderViewSet
    viewset = OrderViewSet()

    # Gọi function gửi email
    result = viewset._send_order_confirmation_email(order)
    print(f"Email result: {result}")

if __name__ == "__main__":
    test_email_debug()
