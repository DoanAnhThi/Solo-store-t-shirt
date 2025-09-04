# Email Configuration Guide - Cwish Store

## Tổng quan

Hệ thống đã được cấu hình để tự động gửi email xác nhận đơn hàng sau khi:
1. Người dùng thanh toán thành công
2. Đơn hàng được tạo thành công
3. Request được gửi đến Shirtigo API

## Cấu hình Email

### Development (Console Backend)
Hiện tại hệ thống đang sử dụng `console.EmailBackend` - email sẽ được in ra console thay vì gửi thực tế.

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Production (SMTP Gmail)

Để cấu hình gửi email thực tế qua Gmail:

1. **Cập nhật settings.py:**
```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Email settings
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'  # Thay bằng email thật
EMAIL_HOST_PASSWORD = 'your-app-password'  # Thay bằng App Password
DEFAULT_FROM_EMAIL = 'Cwish Store <noreply@cwishstore.com>'
```

2. **Tạo App Password cho Gmail:**
   - Vào [Google Account Settings](https://myaccount.google.com/)
   - Bật 2-Factor Authentication
   - Tạo App Password tại: Security > App passwords
   - Sử dụng App Password (không phải mật khẩu chính)

3. **Các provider email khác:**
   ```python
   # Outlook/Hotmail
   EMAIL_HOST = 'smtp-mail.outlook.com'
   EMAIL_PORT = 587

   # Yahoo
   EMAIL_HOST = 'smtp.mail.yahoo.com'
   EMAIL_PORT = 587

   # Custom SMTP
   EMAIL_HOST = 'your-smtp-server.com'
   EMAIL_PORT = 587  # hoặc 465 cho SSL
   EMAIL_USE_SSL = True  # nếu dùng port 465
   ```

## Email Template

Email template được lưu tại: `templates/emails/order_confirmation.html`

Template bao gồm:
- ✅ Logo và header
- ✅ Thông tin đơn hàng (ID, ngày, trạng thái)
- ✅ Chi tiết sản phẩm (hình ảnh, tên, giá)
- ✅ Thông tin giao hàng
- ✅ Production Order ID (từ Shirtigo)
- ✅ Styling responsive

## Flow Gửi Email

```python
# Trong OrderViewSet.create()
1. Tạo đơn hàng
2. Gửi đến Shirtigo API
3. Cập nhật order với Shirtigo response
4. Gửi email xác nhận (mới thêm)
5. Trả về response
```

## Test Email

### Test thủ công:
```bash
cd cwish_backend
python manage.py shell

# Trong shell
from store.views import OrderViewSet
from store.models import Order

order = Order.objects.last()  # Lấy order cuối cùng
viewset = OrderViewSet()
viewset._send_order_confirmation_email(order)
```

### Test qua API:
```bash
# POST /api/orders/test_create/
curl -X POST http://localhost:8000/api/orders/test_create/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'
```

## Troubleshooting

### Email không gửi được:
1. Kiểm tra EMAIL_BACKEND trong settings.py
2. Verify thông tin SMTP
3. Kiểm tra firewall/antivirus
4. Test với email khác

### Template không load:
1. Kiểm tra đường dẫn `templates/emails/order_confirmation.html`
2. Verify TEMPLATES setting trong settings.py
3. Restart Django server

### Lỗi SMTP:
- Gmail: Kiểm tra App Password
- Other providers: Verify credentials và port

## Bảo mật

⚠️ **Quan trọng:**
- Không commit thông tin email/password vào Git
- Sử dụng environment variables cho production:
```python
import os
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
```

## Support

Nếu gặp vấn đề với cấu hình email, kiểm tra:
1. Django email documentation
2. SMTP provider documentation
3. Server logs cho error messages
