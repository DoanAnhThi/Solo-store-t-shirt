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
    print_position = models.CharField(max_length=50, blank=True, null=True, help_text="Position to print on the product (e.g., Front, Back, Left Sleeve)")
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
    print_position = models.CharField(max_length=50, blank=True, null=True, help_text="Selected print position for this cart item")
    personalization = models.TextField(max_length=256, blank=True, null=True, help_text="Personalization text for this cart item")
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


class OrderItem(models.Model):
    """Chi tiết sản phẩm trong đơn hàng - hỗ trợ multiple products"""
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='order_items')

    # Có thể là SingleProduct hoặc DigitalBonusProduct
    product_type = models.CharField(max_length=20, choices=[
        ('single', 'Single Product'),
        ('bonus', 'Bonus Product')
    ])

    # Foreign keys đến các loại sản phẩm (chỉ một trong hai sẽ được set)
    single_product = models.ForeignKey(SingleProduct, on_delete=models.CASCADE, null=True, blank=True)
    bonus_product = models.ForeignKey(DigitalBonusProduct, on_delete=models.CASCADE, null=True, blank=True)

    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    total_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    # Print position for main products (only applicable for single products)
    print_position = models.CharField(max_length=50, blank=True, null=True, help_text="Selected print position for this order item")

    # Personalization for order items
    personalization = models.TextField(max_length=256, blank=True, null=True, help_text="Personalization text for this order item")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self):
        product_name = self.get_product_name()
        return f"{product_name} x {self.quantity}"

    @property
    def product(self):
        """Trả về sản phẩm tương ứng"""
        return self.single_product or self.bonus_product

    def get_product_name(self):
        """Trả về tên sản phẩm"""
        if self.single_product:
            return self.single_product.name
        elif self.bonus_product:
            return self.bonus_product.name
        return "Unknown Product"

    def get_product_image(self):
        """Trả về ảnh sản phẩm"""
        if self.single_product and self.single_product.image:
            return self.single_product.image
        elif self.bonus_product and self.bonus_product.image:
            return self.bonus_product.image
        return None

    def save(self, *args, **kwargs):
        if not self.total_price and self.unit_price is not None:
            self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def clean(self):
        """Validation để đảm bảo chỉ có một loại sản phẩm được chọn"""
        from django.core.exceptions import ValidationError

        if not self.single_product and not self.bonus_product:
            raise ValidationError('Either single_product or bonus_product must be specified')

        if self.single_product and self.bonus_product:
            raise ValidationError('Cannot have both single_product and bonus_product')


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

    # Thông tin tổng quan đơn hàng
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

    # Print position từ order items (computed field)
    print_position = models.CharField(max_length=50, blank=True, null=True, help_text="Print position from order items")

    # Personalization field
    personalization = models.TextField(max_length=256, blank=True, null=True, help_text="Custom personalization text from customer")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.id} - {self.user.username} - {self.get_total_quantity()} items"

    @property
    def quantity(self):
        """Tính tổng quantity của tất cả items"""
        return sum(item.quantity for item in self.order_items.all())

    def get_total_quantity(self):
        """Trả về tổng số lượng sản phẩm"""
        return self.quantity

    def calculate_total_amount(self):
        """Tính lại tổng tiền từ các order items"""
        return sum(item.total_price for item in self.order_items.all())

    def update_total_amount(self):
        """Cập nhật total_amount từ các order items"""
        self.total_amount = self.calculate_total_amount()
        self.save(update_fields=['total_amount'])

    def get_main_products(self):
        """Trả về danh sách main products"""
        return self.order_items.filter(product_type='single')

    def get_bonus_products(self):
        """Trả về danh sách bonus products"""
        return self.order_items.filter(product_type='bonus')

    def update_print_position_and_personalization(self):
        """Cập nhật print_position và personalization từ cart data"""
        # Get print position from order items (only for single products)
        print_positions = []
        personalizations = []

        for item in self.order_items.filter(product_type='single'):
            if item.print_position:
                print_positions.append(item.print_position)
            if item.personalization:
                personalizations.append(item.personalization)

        # Combine unique print positions
        if print_positions:
            self.print_position = ', '.join(set(print_positions))

        # Combine personalizations (if multiple, join them)
        if personalizations:
            self.personalization = ' | '.join(set(personalizations))

        # Save the order
        self.save(update_fields=['print_position', 'personalization'])

    def update_status_after_payment(self):
        """Cập nhật status thành processing sau khi thanh toán thành công"""
        if self.status == 'pending':
            self.status = 'processing'
            self.save(update_fields=['status'])


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
