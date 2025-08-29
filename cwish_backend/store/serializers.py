from rest_framework import serializers
from .models import SingleProduct, UserCart, Order, Contact, DigitalBonusProduct, BonusCart


class SingleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = SingleProduct
        fields = ['id', 'name', 'description', 'price', 'currency', 'image', 'is_active']


class DigitalBonusProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = DigitalBonusProduct
        fields = ['id', 'name', 'description', 'price', 'currency', 'image', 'is_active', 'is_digital']


class UserCartSerializer(serializers.ModelSerializer):
    product = SingleProductSerializer(read_only=True)
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = UserCart
        fields = ['id', 'product', 'quantity', 'total_price', 'created_at', 'updated_at']


class BonusCartSerializer(serializers.ModelSerializer):
    product = DigitalBonusProductSerializer(read_only=True)
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = BonusCart
        fields = ['id', 'product', 'quantity', 'total_price', 'created_at', 'updated_at']


class AddToCartSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1, default=1)


class UpdateCartQuantitySerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=0)  # Cho phép 0 để xóa sản phẩm


class AddBonusToCartSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1, default=1)


class UpdateBonusCartQuantitySerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=0)  # Cho phép 0 để xóa sản phẩm


class OrderSerializer(serializers.ModelSerializer):
    main_product = SingleProductSerializer(read_only=True)
    bonus_product = DigitalBonusProductSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'main_product', 'bonus_product', 'quantity', 'unit_price', 'total_amount', 'currency',
            'email', 'first_name', 'last_name', 'address', 'city', 'country', 'postal_code', 
            'phone', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'unit_price', 'total_amount', 'created_at', 'updated_at']


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
        
        if not main_cart_items.exists() and not bonus_cart_items.exists():
            raise serializers.ValidationError("No items in cart")
        
        orders = []
        
        # Tạo đơn hàng cho sản phẩm chính
        for cart_item in main_cart_items:
            order = Order.objects.create(
                user=user,
                product=cart_item.product,
                quantity=cart_item.quantity,
                unit_price=cart_item.product.price,
                total_amount=cart_item.total_price,
                **validated_data
            )
            orders.append(order)
        
        # Tạo đơn hàng cho sản phẩm bonus
        for cart_item in bonus_cart_items:
            order = Order.objects.create(
                user=user,
                product=cart_item.product,
                quantity=cart_item.quantity,
                unit_price=cart_item.product.price,
                total_amount=cart_item.total_price,
                **validated_data
            )
            orders.append(order)
        
        # Xóa giỏ hàng sau khi đặt hàng
        main_cart_items.delete()
        bonus_cart_items.delete()
        
        return orders[0] if len(orders) == 1 else orders


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone', 'message']
    
    def create(self, validated_data):
        return Contact.objects.create(**validated_data)
