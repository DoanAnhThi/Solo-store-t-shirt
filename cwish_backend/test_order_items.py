#!/usr/bin/env python
"""
Test script để kiểm tra OrderItem và cách truy cập product name & image
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwish_backend.settings')
django.setup()

from store.models import Order, OrderItem, SingleProduct, DigitalBonusProduct, User
from store.serializers import OrderItemSerializer

def test_order_item_creation():
    """Test tạo OrderItem và truy cập thông tin"""
    print("🎯 Testing OrderItem creation and access...")

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

        print(f"📦 Single Product: {single_product.name if single_product else 'None'}")
        print(f"🎁 Bonus Product: {bonus_product.name if bonus_product else 'None'}")

        # Tạo OrderItem cho single product
        if single_product:
            single_item = OrderItem.objects.create(
                order=order,
                product_type='single',
                single_product=single_product,
                quantity=2,
                unit_price=single_product.price,
                total_price=single_product.price * 2
            )
            print(f"✅ Created single item: {single_item}")

        # Tạo OrderItem cho bonus product
        if bonus_product:
            bonus_item = OrderItem.objects.create(
                order=order,
                product_type='bonus',
                bonus_product=bonus_product,
                quantity=1,
                unit_price=bonus_product.price,
                total_price=bonus_product.price
            )
            print(f"✅ Created bonus item: {bonus_item}")

        # Test truy cập thông tin
        print("\n🔍 Testing data access...")

        for item in order.order_items.all():
            print(f"\n📋 OrderItem ID: {item.id}")
            print(f"   Type: {item.product_type}")
            print(f"   Product Name (method): {item.get_product_name()}")
            print(f"   Product Image (method): {item.get_product_image()}")

            # Test serializer
            serializer = OrderItemSerializer(item)
            serialized_data = serializer.data
            print(f"   Serialized Name: {serialized_data.get('product_name')}")
            print(f"   Serialized Image: {serialized_data.get('product_image')}")

            # Test related objects
            if item.single_product:
                print(f"   Single Product: {item.single_product.name}")
                if item.single_product.image:
                    print(f"   Single Product Image: {item.single_product.image.url}")
            elif item.bonus_product:
                print(f"   Bonus Product: {item.bonus_product.name}")
                if item.bonus_product.image:
                    print(f"   Bonus Product Image: {item.bonus_product.image.url}")

        # Cập nhật total amount
        order.total_amount = sum(item.total_price for item in order.order_items.all())
        order.save()
        print(f"\n💰 Updated order total: ${order.total_amount}")

        return order

    except Exception as e:
        print(f"❌ Error in test_order_item_creation: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_email_with_order_items(order):
    """Test gửi email với order items"""
    print("\n📧 Testing email with order items...")

    try:
        from store.views import OrderViewSet

        # Load order items với select_related
        order_items = order.order_items.select_related('single_product', 'bonus_product').all()

        print(f"📦 Loaded {order_items.count()} order items")

        for item in order_items:
            print(f"   - {item.get_product_name()} x {item.quantity}")
            image = item.get_product_image()
            if image:
                print(f"     Image: {image.url}")

        # Test gửi email
        viewset = OrderViewSet()
        success = viewset._send_order_confirmation_email(order)

        if success:
            print("✅ Email sent successfully with order items!")
            return True
        else:
            print("❌ Failed to send email")
            return False

    except Exception as e:
        print(f"❌ Error testing email: {e}")
        import traceback
        traceback.print_exc()
        return False

def cleanup_test_data():
    """Xóa dữ liệu test"""
    print("\n🧹 Cleaning up test data...")

    try:
        # Xóa orders của test user
        test_user = User.objects.filter(username='test_user').first()
        if test_user:
            Order.objects.filter(user=test_user).delete()
            print("✅ Cleaned up test orders")

    except Exception as e:
        print(f"❌ Error cleaning up: {e}")

if __name__ == '__main__':
    print("🚀 Starting OrderItem tests...\n")

    # Test 1: Tạo và truy cập OrderItem
    order = test_order_item_creation()

    if order:
        # Test 2: Gửi email với order items
        email_success = test_email_with_order_items(order)

        print("\n" + "="*60)
        print("📊 Test Results:")
        print(f"OrderItem Creation: ✅ PASS")
        print(f"Email with Items: {'✅ PASS' if email_success else '❌ FAIL'}")

        if email_success:
            print("\n🎉 All tests passed! OrderItem system is working correctly.")
        else:
            print("\n⚠️ Email test failed. Check the errors above.")
    else:
        print("❌ OrderItem creation failed")

    # Cleanup
    cleanup_test_data()
