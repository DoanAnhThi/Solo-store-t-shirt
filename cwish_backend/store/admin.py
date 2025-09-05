from django.contrib import admin
from .models import SingleProduct, UserCart, Order, Contact, DigitalBonusProduct, BonusCart, OrderItem


@admin.register(SingleProduct)
class SingleProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'currency', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(DigitalBonusProduct)
class DigitalBonusProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'currency', 'is_active', 'is_digital', 'created_at']
    list_filter = ['is_active', 'is_digital', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserCart)
class UserCartAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'quantity', 'total_price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email', 'product__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(BonusCart)
class BonusCartAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'quantity', 'total_price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email', 'product__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'get_product_names', 'get_quantity', 'total_amount', 'currency', 'status', 'print_position', 'personalization', 'created_at']
    list_filter = ['status', 'created_at', 'country']
    search_fields = ['user__username', 'user__email', 'first_name', 'last_name', 'email']
    readonly_fields = ['id', 'created_at', 'updated_at', 'get_product_names', 'get_quantity', 'print_position', 'personalization']

    def get_product_names(self, obj):
        """Display product names from OrderItems"""
        products = []
        for item in obj.order_items.all():
            if item.single_product:
                product_name = f"Main: {item.single_product.name} (x{item.quantity})"
                if item.print_position:
                    product_name += f" - {item.print_position}"
                products.append(product_name)
            elif item.bonus_product:
                products.append(f"Bonus: {item.bonus_product.name} (x{item.quantity})")

        return "; ".join(products) if products else 'N/A'
    get_product_names.short_description = 'Products'

    def get_quantity(self, obj):
        """Display total quantity"""
        return obj.quantity
    get_quantity.short_description = 'Total Quantity'

    fieldsets = (
        ('Order Information', {
            'fields': ('id', 'user', 'get_product_names', 'get_quantity', 'total_amount', 'currency', 'status', 'print_position', 'personalization', 'shirtigo_order_id')
        }),
        ('Customer Information', {
            'fields': ('email', 'first_name', 'last_name', 'phone')
        }),
        ('Shipping Address', {
            'fields': ('address', 'city', 'country', 'postal_code')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_type', 'get_product_name', 'quantity', 'unit_price', 'total_price', 'print_position', 'personalization', 'created_at']
    list_filter = ['product_type', 'created_at']
    search_fields = ['order__id', 'single_product__name', 'bonus_product__name']
    readonly_fields = ['created_at']

    def get_product_name(self, obj):
        """Display product name based on product type"""
        if obj.single_product:
            return obj.single_product.name
        elif obj.bonus_product:
            return obj.bonus_product.name
        return 'N/A'
    get_product_name.short_description = 'Product Name'


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'message']
    readonly_fields = ['created_at']
    list_editable = ['is_read']

    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone', 'message')
        }),
        ('Status', {
            'fields': ('is_read',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
