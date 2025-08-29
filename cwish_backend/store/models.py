from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
import uuid


class SingleProduct(models.Model):
    """Model cho sản phẩm duy nhất của website"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default='USD')
    image = models.ImageField(upload_to='product/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Single Product"
        verbose_name_plural = "Single Product"


class DigitalBonusProduct(models.Model):
    """Model cho sản phẩm digital bonus"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default='USD')
    image = models.ImageField(upload_to='product/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_digital = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Digital Bonus Product"
        verbose_name_plural = "Digital Bonus Products"


class UserCart(models.Model):
    """Giỏ hàng của từng user"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart')
    product = models.ForeignKey(SingleProduct, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'product']
        verbose_name = "User Cart"
        verbose_name_plural = "User Carts"

    def __str__(self):
        return f"{self.user.username} - {self.product.name} x {self.quantity}"

    @property
    def total_price(self):
        return self.quantity * self.product.price


class BonusCart(models.Model):
    """Giỏ hàng riêng cho sản phẩm bonus"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bonus_cart')
    product = models.ForeignKey(DigitalBonusProduct, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'product']
        verbose_name = "Bonus Cart"
        verbose_name_plural = "Bonus Carts"

    def __str__(self):
        return f"{self.user.username} - {self.product.name} x {self.quantity}"

    @property
    def total_price(self):
        return self.quantity * self.product.price


class Order(models.Model):
    """Đơn hàng"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    
    # Sản phẩm có thể là SingleProduct hoặc DigitalBonusProduct
    main_product = models.ForeignKey(SingleProduct, on_delete=models.CASCADE, null=True, blank=True)
    bonus_product = models.ForeignKey(DigitalBonusProduct, on_delete=models.CASCADE, null=True, blank=True)
    
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default='USD')
    
    # Thông tin giao hàng
    email = models.EmailField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=20, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Thông tin Shirtigo
    shirtigo_order_id = models.CharField(max_length=100, blank=True, null=True)
    shirtigo_response = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        product_name = self.main_product.name if self.main_product else self.bonus_product.name
        return f"Order {self.id} - {self.user.username} - {product_name}"

    @property
    def product(self):
        """Trả về sản phẩm tương ứng"""
        return self.main_product or self.bonus_product

    def save(self, *args, **kwargs):
        if not self.total_amount and self.unit_price is not None:
            self.total_amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def clean(self):
        """Validation để đảm bảo chỉ có một loại sản phẩm được chọn"""
        from django.core.exceptions import ValidationError
        
        if not self.main_product and not self.bonus_product:
            raise ValidationError('Either main_product or bonus_product must be specified')
        
        if self.main_product and self.bonus_product:
            raise ValidationError('Cannot have both main_product and bonus_product')


class Contact(models.Model):
    """Model lưu thông tin liên hệ từ form contact"""
    name = models.CharField(max_length=200, verbose_name="Tên")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Số điện thoại")
    message = models.TextField(verbose_name="Tin nhắn")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    is_read = models.BooleanField(default=False, verbose_name="Đã đọc")
    
    class Meta:
        verbose_name = "Liên hệ"
        verbose_name_plural = "Liên hệ"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.email} - {self.created_at.strftime('%d/%m/%Y')}"
