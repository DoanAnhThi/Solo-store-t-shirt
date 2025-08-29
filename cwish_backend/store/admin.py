from django.contrib import admin
from .models import SingleProduct, UserCart, Order, Contact, DigitalBonusProduct, BonusCart


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
    list_display = ['id', 'user', 'get_product_name', 'quantity', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'country']
    search_fields = ['user__username', 'user__email', 'first_name', 'last_name', 'email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def get_product_name(self, obj):
        if obj.main_product:
            return f"Main: {obj.main_product.name}"
        elif obj.bonus_product:
            return f"Bonus: {obj.bonus_product.name}"
        return 'N/A'
    get_product_name.short_description = 'Product'
    
    fieldsets = (
        ('Order Information', {
            'fields': ('id', 'user', 'main_product', 'bonus_product', 'quantity', 'unit_price', 'total_amount', 'currency', 'status')
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
