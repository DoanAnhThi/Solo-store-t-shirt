#!/usr/bin/env python
"""
Test script để kiểm tra ảnh trong email có hiển thị đúng không
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwish_backend.settings')
django.setup()

from django.template.loader import render_to_string
from store.models import Order, OrderItem, SingleProduct, DigitalBonusProduct, User
from store.serializers import OrderItemSerializer
from django.conf import settings

def create_test_order_with_images():
    """Tạo order test với images để test email"""
    print("🎯 Creating test order with images...")

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
            print(f"✅ Single product: {single_product.name}")
            if single_product.image:
                print(f"   Image: {single_product.image.url}")

        if bonus_product:
            OrderItem.objects.create(
                order=order,
                product_type='bonus',
                bonus_product=bonus_product,
                quantity=1,
                unit_price=bonus_product.price,
                total_price=bonus_product.price
            )
            print(f"✅ Bonus product: {bonus_product.name}")
            if bonus_product.image:
                print(f"   Image: {bonus_product.image.url}")

        # Cập nhật total
        order.total_amount = sum(item.total_price for item in order.order_items.all())
        order.save()

        return order

    except Exception as e:
        print(f"❌ Error creating test order: {e}")
        return None

def test_email_image_urls(order):
    """Test URL ảnh trong email"""
    print("\n🖼️ Testing email image URLs...")

    try:
        # Load order items
        order_items = order.order_items.select_related('single_product', 'bonus_product').all()

        # Serialize với context
        serializer = OrderItemSerializer(order_items, many=True, context={'request': None})
        serialized_items = serializer.data

        print(f"📦 Serialized {len(serialized_items)} items")

        for i, item in enumerate(serialized_items):
            print(f"\n📋 Item {i+1}:")
            print(f"   Name: {item.get('product_name')}")
            print(f"   Image URL: {item.get('product_image')}")

            # Kiểm tra URL có phải absolute không
            image_url = item.get('product_image')
            if image_url:
                if image_url.startswith('http'):
                    print(f"   ✅ Absolute URL: {image_url}")
                else:
                    print(f"   ⚠️ Relative URL: {image_url}")
            else:
                print("   ❌ No image URL")

        # Render template
        html_content = render_to_string('emails/order_confirmation.html', {
            'order': order,
            'order_items': serialized_items,
            'site_url': settings.SITE_URL,
        })

        print("\n📧 Template rendered successfully!")
        print(f"Site URL: {settings.SITE_URL}")

        # Tìm kiếm image URLs trong HTML
        import re
        image_matches = re.findall(r'<img[^>]*src="([^"]*)"[^>]*>', html_content)
        print(f"\n🖼️ Image URLs found in email HTML: {len(image_matches)}")

        for i, url in enumerate(image_matches):
            print(f"   {i+1}. {url}")
            if url.startswith('http'):
                print("      ✅ Absolute URL")
            else:
                print("      ⚠️ Relative URL")

        return True

    except Exception as e:
        print(f"❌ Error testing email images: {e}")
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
    print("🚀 Email Image Test\n")

    # Tạo order test
    order = create_test_order_with_images()

    if order:
        # Test image URLs
        success = test_email_image_urls(order)

        if success:
            print("\n🎉 Email image test completed!")
            print("📧 Check the URLs above - they should be absolute URLs for email clients.")
        else:
            print("\n❌ Email image test failed.")
    else:
        print("❌ Failed to create test order")

    # Cleanup
    cleanup()
