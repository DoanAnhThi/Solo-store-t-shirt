# PayPal Integration Setup Guide

## Tổng quan
Hệ thống thanh toán PayPal đã được tích hợp vào trang checkout của T-shirt Store. Người dùng có thể thanh toán an toàn thông qua PayPal sau khi hoàn thành form thông tin giao hàng.

## Tính năng chính

### 1. Trang Checkout
- Form thông tin giao hàng đầy đủ
- Hiển thị tổng quan đơn hàng
- Tích hợp nút thanh toán PayPal
- Validation form trước khi thanh toán
- Lưu trữ dữ liệu form tự động

### 2. Tích hợp PayPal
- PayPal Smart Payment Buttons
- Xử lý thanh toán tự động
- Capture payment ngay lập tức
- Xử lý lỗi và hủy thanh toán
- Lưu trữ thông tin đơn hàng

### 3. Quản lý đơn hàng
- Lưu trữ đơn hàng vào backend (nếu có)
- Lưu trữ local fallback
- Tự động xóa giỏ hàng sau khi thanh toán thành công
- Tạo Order ID duy nhất

## Cài đặt và cấu hình

### Bước 1: Tạo PayPal Developer Account
1. Truy cập [PayPal Developer Portal](https://developer.paypal.com/)
2. Đăng ký tài khoản developer
3. Tạo ứng dụng mới để lấy Client ID

### Bước 2: Cấu hình PayPal Client ID
1. Mở file `paypal-integration.js`
2. Thay thế `YOUR_PAYPAL_CLIENT_ID` bằng Client ID thực tế:

```javascript
constructor() {
    this.paypalClientId = 'YOUR_ACTUAL_CLIENT_ID_HERE';
    this.environment = 'sandbox'; // 'sandbox' cho testing, 'production' cho live
    this.init();
}
```

### Bước 3: Cấu hình Environment
- **Sandbox**: Sử dụng cho testing và development
- **Production**: Sử dụng cho website thực tế

```javascript
this.environment = 'sandbox'; // Thay đổi thành 'production' khi deploy
```

## Cấu trúc file

### 1. `checkout.html`
- Trang thanh toán chính
- Form thông tin khách hàng
- Hiển thị tổng quan đơn hàng
- Container cho PayPal buttons

### 2. `paypal-integration.js`
- Class PayPalIntegration
- Xử lý toàn bộ logic PayPal
- Tạo và xử lý đơn hàng
- Quản lý trạng thái thanh toán

### 3. `cart-manager.js`
- Quản lý giỏ hàng
- Lưu trữ dữ liệu giỏ hàng vào sessionStorage
- Đồng bộ với backend

### 4. `partials/minicart.html`
- Mini cart hiển thị
- Nút checkout dẫn đến trang thanh toán

## Luồng thanh toán

### 1. Người dùng nhấn Checkout
```
Minicart → checkout.html
```

### 2. Điền thông tin giao hàng
- Form validation tự động
- Lưu trữ dữ liệu vào localStorage

### 3. Thanh toán PayPal
- Validation form trước khi tạo order
- Tạo PayPal order với thông tin đầy đủ
- Chuyển hướng đến PayPal để xác nhận

### 4. Xử lý kết quả
- **Thành công**: Lưu đơn hàng, xóa giỏ hàng, hiển thị thông báo
- **Lỗi**: Hiển thị thông báo lỗi, cho phép thử lại
- **Hủy**: Hiển thị thông báo hủy

## API Endpoints

### Backend (nếu có)
```
POST /api/orders/create/
Content-Type: application/json
Body: Order data với PayPal transaction details
```

### Local Storage
- `cartData`: Dữ liệu giỏ hàng
- `checkoutFormData`: Dữ liệu form đã điền
- `orders`: Danh sách đơn hàng đã thanh toán

## Xử lý lỗi

### 1. PayPal SDK không load
- Kiểm tra internet connection
- Kiểm tra Client ID
- Refresh trang

### 2. Form validation
- Tất cả trường bắt buộc phải được điền
- Email format hợp lệ
- Phone number hợp lệ

### 3. Thanh toán thất bại
- Kiểm tra thông tin thẻ/account PayPal
- Thử lại hoặc liên hệ support

## Testing

### Sandbox Mode
1. Sử dụng tài khoản PayPal sandbox
2. Test với thẻ giả
3. Kiểm tra các trường hợp lỗi

### Test Cases
- [ ] Form validation
- [ ] PayPal order creation
- [ ] Payment success flow
- [ ] Payment error handling
- [ ] Payment cancellation
- [ ] Order data storage
- [ ] Cart clearing

## Security Considerations

### 1. Client ID
- Không commit Client ID thật vào git
- Sử dụng environment variables
- Restrict Client ID theo domain

### 2. Data Validation
- Validate tất cả input từ user
- Sanitize data trước khi gửi đến PayPal
- Kiểm tra CSRF token

### 3. HTTPS
- Luôn sử dụng HTTPS trong production
- PayPal yêu cầu HTTPS cho production

## Deployment

### 1. Production Checklist
- [ ] Thay đổi environment từ 'sandbox' sang 'production'
- [ ] Cập nhật PayPal Client ID production
- [ ] Kiểm tra HTTPS
- [ ] Test toàn bộ flow thanh toán
- [ ] Backup dữ liệu

### 2. Environment Variables
```bash
PAYPAL_CLIENT_ID=your_production_client_id
PAYPAL_ENVIRONMENT=production
```

## Troubleshooting

### Vấn đề thường gặp

#### 1. PayPal buttons không hiển thị
- Kiểm tra console errors
- Kiểm tra PayPal SDK load
- Kiểm tra Client ID

#### 2. Form validation không hoạt động
- Kiểm tra JavaScript errors
- Kiểm tra field IDs
- Kiểm tra validateForm function

#### 3. Thanh toán không thành công
- Kiểm tra PayPal account
- Kiểm tra network connection
- Kiểm tra console errors

### Debug Mode
```javascript
// Thêm vào paypal-integration.js để debug
console.log('PayPal Integration Debug Mode');
console.log('Cart Data:', this.getCartData());
console.log('Customer Data:', this.getCustomerData());
```

## Support

### Tài liệu tham khảo
- [PayPal Developer Documentation](https://developer.paypal.com/docs/)
- [PayPal JavaScript SDK](https://developer.paypal.com/docs/checkout/)
- [PayPal REST API](https://developer.paypal.com/docs/api/)

### Liên hệ
- PayPal Developer Support: [developer.paypal.com/support](https://developer.paypal.com/support)
- Technical Issues: Kiểm tra console logs và network tab

## Changelog

### Version 1.0.0
- Tích hợp PayPal Smart Payment Buttons
- Form validation và auto-save
- Xử lý thanh toán tự động
- Lưu trữ đơn hàng local/backend
- Responsive design cho mobile

---

**Lưu ý**: Đây là phiên bản đầu tiên của PayPal integration. Hãy test kỹ trước khi deploy lên production.
