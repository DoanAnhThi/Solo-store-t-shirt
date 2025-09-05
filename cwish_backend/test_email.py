#!/usr/bin/env python
"""
Test script để kiểm tra email template và logic gửi email
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwish_backend.settings')
django.setup()

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from store.models import Order, OrderItem, SingleProduct, DigitalBonusProduct

def test_email_template():
    """Test email template với dữ liệu giả"""
    print("🎯 Testing email template...")

    try:
        # Tạo dữ liệu test
        order_data = {
            'id': 'TEST-123',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'total_amount': 45.99,
            'currency': 'USD',
            'created_at': '2024-01-15 10:30:00',
            'get_status_display': lambda: 'Processing',
        }

        # Tạo order items giả
        order_items = [
            {
                'product_name': 'Test T-Shirt',
                'product_type': 'single',
                'quantity': 2,
                'unit_price': 15.99,
                'total_price': 31.98,
                'single_product': type('obj', (object,), {'image': type('obj', (object,), {'url': '/media/product/test.jpg'})()})(),
                'bonus_product': None,
                'product_image': '/media/product/test.jpg'
            },
            {
                'product_name': 'Bonus Digital Product',
                'product_type': 'bonus',
                'quantity': 1,
                'unit_price': 14.01,
                'total_price': 14.01,
                'single_product': None,
                'bonus_product': type('obj', (object,), {'image': type('obj', (object,), {'url': '/media/product/bonus.jpg'})()})(),
                'product_image': '/media/product/bonus.jpg'
            }
        ]

        # Render template
        html_content = render_to_string('emails/order_confirmation.html', {
            'order': type('Order', (), order_data)(),
            'order_items': order_items,
        })

        print("✅ Template rendered successfully!")
        print(f"📄 Email content length: {len(html_content)} characters")

        # Tạo subject
        subject = f'Order Confirmation - Order #{order_data["id"]} - Cwish Store'

        # Tạo email (nhưng không gửi)
        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email='Cwish Store <noreply@cwishstore.com>',
            to=['test@example.com'],
        )
        email.content_subtype = 'html'

        print("✅ Email object created successfully!")
        print(f"📧 Subject: {subject}")
        print(f"📧 To: {email.to}")
        print(f"📧 From: {email.from_email}")

        # Hiển thị một phần nội dung email
        print("\n📋 Email Preview (first 500 chars):")
        print("-" * 50)
        print(html_content[:500] + "...")
        print("-" * 50)

        return True

    except Exception as e:
        print(f"❌ Error testing email template: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_real_order():
    """Test với một order thực từ database"""
    print("\n🎯 Testing with real order from database...")

    try:
        # Lấy order cuối cùng
        order = Order.objects.last()
        if not order:
            print("❌ No orders found in database")
            return False

        print(f"📦 Found order: {order.id}")
        print(f"👤 Customer: {order.first_name} {order.last_name}")
        print(f"📧 Email: {order.email}")
        print(f"💰 Total: ${order.total_amount}")

        # Lấy order items
        order_items = order.order_items.select_related('single_product', 'bonus_product').all()
        print(f"📦 Order items count: {order_items.count()}")

        for item in order_items:
            print(f"   - {item.product_name} x {item.quantity} = ${item.total_price}")

        # Test gửi email
        from store.views import OrderViewSet
        viewset = OrderViewSet()

        print("\n📧 Sending test email...")
        success = viewset._send_order_confirmation_email(order)

        if success:
            print("✅ Email sent successfully!")
        else:
            print("❌ Failed to send email")

        return success

    except Exception as e:
        print(f"❌ Error testing real order: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 Starting email template tests...\n")

    # Test 1: Template với dữ liệu giả
    template_test = test_email_template()

    print("\n" + "="*60)

    # Test 2: Template với order thực
    real_test = test_real_order()

    print("\n" + "="*60)
    print("📊 Test Results:")
    print(f"Template Test: {'✅ PASS' if template_test else '❌ FAIL'}")
    print(f"Real Order Test: {'✅ PASS' if real_test else '❌ FAIL'}")

    if template_test and real_test:
        print("\n🎉 All tests passed! Email system is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")
