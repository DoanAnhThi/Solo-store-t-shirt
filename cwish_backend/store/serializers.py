from rest_framework import serializers
from .models import SingleProduct, UserCart, Order, Contact, DigitalBonusProduct, BonusCart, OrderItem


class SingleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = SingleProduct
        fields = ['id', 'name', 'description', 'price', 'currency', 'image', 'is_active', 'print_position']


class DigitalBonusProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = DigitalBonusProduct
        fields = ['id', 'name', 'description', 'price', 'currency', 'image', 'is_active', 'is_digital']


class UserCartSerializer(serializers.ModelSerializer):
    product = SingleProductSerializer(read_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = UserCart
        fields = ['id', 'product', 'quantity', 'total_price', 'print_position', 'personalization', 'created_at', 'updated_at']


class BonusCartSerializer(serializers.ModelSerializer):
    product = DigitalBonusProductSerializer(read_only=True)
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = BonusCart
        fields = ['id', 'product', 'quantity', 'total_price', 'created_at', 'updated_at']


class AddToCartSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1, default=1)
    print_position = serializers.CharField(max_length=50, required=False, allow_blank=True)
    personalization = serializers.CharField(max_length=256, required=False, allow_blank=True)


class UpdateCartQuantitySerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=0)  # Cho phép 0 để xóa sản phẩm


class AddBonusToCartSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1, default=1)


class UpdateBonusCartQuantitySerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=0)  # Cho phép 0 để xóa sản phẩm


class OrderItemSerializer(serializers.ModelSerializer):
    single_product = SingleProductSerializer(read_only=True)
    bonus_product = DigitalBonusProductSerializer(read_only=True)
    product_name = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product_type', 'single_product', 'bonus_product',
            'quantity', 'unit_price', 'total_price', 'print_position', 'personalization', 'product_name', 'product_image'
        ]

    def get_product_name(self, obj):
        return obj.get_product_name()

    def get_product_image(self, obj):
        image = obj.get_product_image()
        if image:
            # Trả về URL tuyệt đối cho email
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(image.url)
            else:
                # Fallback nếu không có request context
                from django.conf import settings
                return f"{settings.SITE_URL}{image.url}"
        return None


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    quantity = serializers.ReadOnlyField()
    main_products = serializers.SerializerMethodField()
    bonus_products = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'order_items', 'quantity', 'total_amount', 'currency',
            'email', 'first_name', 'last_name', 'address', 'city', 'country', 'postal_code',
            'phone', 'status', 'print_position', 'personalization', 'main_products', 'bonus_products',
            'shirtigo_order_id', 'shirtigo_response', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_main_products(self, obj):
        return OrderItemSerializer(obj.get_main_products(), many=True).data

    def get_bonus_products(self, obj):
        return OrderItemSerializer(obj.get_bonus_products(), many=True).data


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'email', 'first_name', 'last_name', 'address',
            'city', 'country', 'postal_code', 'phone'
        ]

    def create(self, validated_data):
        user = self.context['request'].user

        # Lấy sản phẩm chính từ giỏ hàng
        main_cart_items = UserCart.objects.filter(user=user)
        bonus_cart_items = BonusCart.objects.filter(user=user)

        # Nếu giỏ hàng trống, tạo đơn với sản phẩm mặc định (fallback cho frontend hiện tại)
        if not main_cart_items.exists() and not bonus_cart_items.exists():
            request = self.context.get('request')
            payload_items = []
            try:
                payload_items = (request.data.get('items') or []) if request else []
            except Exception:
                payload_items = []

            # Lấy sản phẩm đang active (website 1 sản phẩm)
            main_product = SingleProduct.objects.filter(is_active=True).first()
            if not main_product:
                raise serializers.ValidationError("No active product available")

            quantity = 0
            try:
                for it in payload_items:
                    q = int(it.get('quantity') or 0)
                    quantity += q
            except Exception:
                quantity = 0
            if quantity <= 0:
                quantity = 1

            # Tạo đơn hàng
            order = Order.objects.create(
                user=user,
                total_amount=quantity * main_product.price,
                currency='USD',
                **validated_data
            )

            # Tạo OrderItem cho sản phẩm chính
            OrderItem.objects.create(
                order=order,
                product_type='single',
                single_product=main_product,
                quantity=quantity,
                unit_price=main_product.price,
                total_price=quantity * main_product.price
            )

            return order

        # Tạo đơn hàng mới với nhiều items
        order = Order.objects.create(
            user=user,
            total_amount=0,  # Sẽ được cập nhật sau
            currency='USD',
            **validated_data
        )

        total_amount = 0

        # Thêm main cart items vào order
        for cart_item in main_cart_items:
            OrderItem.objects.create(
                order=order,
                product_type='single',
                single_product=cart_item.product,
                quantity=cart_item.quantity,
                unit_price=cart_item.product.price,
                total_price=cart_item.total_price,
                print_position=cart_item.print_position,
                personalization=cart_item.personalization
            )
            total_amount += cart_item.total_price

        # Thêm bonus cart items vào order
        for cart_item in bonus_cart_items:
            OrderItem.objects.create(
                order=order,
                product_type='bonus',
                bonus_product=cart_item.product,
                quantity=cart_item.quantity,
                unit_price=cart_item.product.price,
                total_price=cart_item.total_price
            )
            total_amount += cart_item.total_price

        # Cập nhật tổng tiền cho order
        order.total_amount = total_amount
        order.save()

        # Cập nhật print_position từ order items
        order.update_print_position_and_personalization()

        # Xóa giỏ hàng sau khi đặt hàng
        main_cart_items.delete()
        bonus_cart_items.delete()

        return order


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone', 'message']
    
    def create(self, validated_data):
        return Contact.objects.create(**validated_data)
