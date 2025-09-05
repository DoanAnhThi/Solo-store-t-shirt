#!/usr/bin/env python
"""
Test cuối cùng để kiểm tra email template với product name và image
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwish_backend.settings')
django.setup()

from django.template.loader import render_to_string
from store.models import Order, OrderItem, SingleProduct, DigitalBonusProduct, User
from store.serializers import OrderItemSerializer

def create_test_order_with_items():
    """Tạo order test với order items để test email"""
    print("🎯 Creating test order with items...")

    try:
        # Lấy user test
        test_user, created = User.objects.get_or_create(
            username='test_user',
            defaults={'email': 'test@example.com'}
        )

        # Tạo order
        order = Order.objects.create(
            user=test_user,
            total_amount=0,
            currency='USD',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            address='123 Test St',
            city='Test City',
            country='VN',
            postal_code='70000'
        )

        # Lấy sản phẩm để test
        single_product = SingleProduct.objects.filter(is_active=True).first()
        bonus_product = DigitalBonusProduct.objects.filter(is_active=True).first()

        if single_product:
            OrderItem.objects.create(
                order=order,
                product_type='single',
                single_product=single_product,
                quantity=2,
                unit_price=single_product.price,
                total_price=single_product.price * 2
            )

        if bonus_product:
            OrderItem.objects.create(
                order=order,
                product_type='bonus',
                bonus_product=bonus_product,
                quantity=1,
                unit_price=bonus_product.price,
                total_price=bonus_product.price
            )

        # Cập nhật total
        order.total_amount = sum(item.total_price for item in order.order_items.all())
        order.save()

        return order

    except Exception as e:
        print(f"❌ Error creating test order: {e}")
        return None

def test_email_template_rendering(order):
    """Test render email template với order items"""
    print("\n📧 Testing email template rendering...")

    try:
        # Load order items
        order_items = order.order_items.select_related('single_product', 'bonus_product').all()

        print(f"📦 Order has {order_items.count()} items")

        # Serialize order items để xem dữ liệu
        serialized_items = []
        for item in order_items:
            serializer = OrderItemSerializer(item)
            serialized_items.append(serializer.data)
            print(f"   Item: {serializer.data.get('product_name')} - Image: {serializer.data.get('product_image')}")

        # Render template
        html_content = render_to_string('emails/order_confirmation.html', {
            'order': order,
            'order_items': serialized_items,  # Sử dụng serialized data
        })

        print("✅ Template rendered successfully!")

        # Tìm kiếm product names trong HTML
        product_names_found = []
        import re
        name_matches = re.findall(r'<h4[^>]*>(.*?)</h4>', html_content, re.DOTALL)
        for match in name_matches:
            # Loại bỏ HTML tags và extra spaces
            clean_name = re.sub(r'<[^>]+>', '', match).strip()
            if clean_name and 'Order Items' not in clean_name and 'Order Information' not in clean_name:
                product_names_found.append(clean_name)

        print(f"📋 Product names found in email: {product_names_found}")

        # Tìm kiếm image URLs
        image_matches = re.findall(r'<img[^>]*src="([^"]*)"[^>]*>', html_content)
        print(f"🖼️ Image URLs found in email: {image_matches}")

        # Hiển thị preview của phần product items
        print("\n📋 Email Product Section Preview:")
        print("-" * 50)

        # Tìm phần Order Items trong HTML
        items_start = html_content.find('<h3>Order Items</h3>')
        if items_start != -1:
            items_end = html_content.find('<div style="border-top: 2px solid #007bff"', items_start)
            if items_end != -1:
                items_section = html_content[items_start:items_end]
                # Hiển thị một phần để kiểm tra
                print(items_section[:1000] + "..." if len(items_section) > 1000 else items_section)

        print("-" * 50)

        return True

    except Exception as e:
        print(f"❌ Error testing email template: {e}")
        import traceback
        traceback.print_exc()
        return False

def cleanup():
    """Dọn dẹp dữ liệu test"""
    try:
        test_user = User.objects.filter(username='test_user').first()
        if test_user:
            Order.objects.filter(user=test_user).delete()
            print("✅ Cleaned up test data")
    except Exception as e:
        print(f"❌ Error cleaning up: {e}")

if __name__ == '__main__':
    print("🚀 Final Email Template Test\n")

    # Tạo order test
    order = create_test_order_with_items()

    if order:
        # Test render template
        success = test_email_template_rendering(order)

        if success:
            print("\n🎉 Email template test completed successfully!")
            print("📧 The email should now display product names and images correctly.")
        else:
            print("\n❌ Email template test failed.")
    else:
        print("❌ Failed to create test order")

    # Cleanup
    cleanup()
