# T-shirt Store - Single Product E-commerce System

## Tổng quan

Đây là một hệ thống e-commerce đơn giản được xây dựng bằng Django backend và HTML/CSS/JavaScript frontend, được thiết kế để bán duy nhất một sản phẩm với khả năng điều chỉnh số lượng.

## Tính năng chính

- **Single Product System**: Chỉ bán duy nhất một sản phẩm
- **User Authentication**: Hệ thống đăng nhập/đăng ký
- **Shopping Cart**: Giỏ hàng riêng biệt cho từng user
- **Quantity Management**: Có thể thêm/bớt số lượng sản phẩm
- **Real-time Updates**: Cập nhật giỏ hàng theo thời gian thực
- **Mini-cart**: Hiển thị giỏ hàng nhỏ gọn

## Cấu trúc dự án

```
T-shirt Store/
├── cwish_backend/          # Django Backend
│   ├── store/             # Django app chính
│   │   ├── models.py      # Database models
│   │   ├── views.py       # API endpoints
│   │   ├── serializers.py # Data serializers
│   │   └── urls.py        # URL routing
│   ├── manage.py          # Django management
│   └── requirements.txt   # Python dependencies
├── cwish-fontend/         # Frontend
│   ├── nectar.html        # Trang sản phẩm chính
│   ├── cart-manager.js    # Cart management logic
│   ├── partials/          # Reusable components
│   └── test-cart-api.html # API testing page
└── docker-compose.yml     # Docker configuration
```

## Models

### SingleProduct
- `name`: Tên sản phẩm
- `description`: Mô tả sản phẩm
- `price`: Giá sản phẩm
- `currency`: Đơn vị tiền tệ
- `image`: Hình ảnh sản phẩm
- `is_active`: Trạng thái hoạt động

### UserCart
- `user`: User sở hữu giỏ hàng
- `product`: Sản phẩm trong giỏ hàng
- `quantity`: Số lượng
- `total_price`: Tổng giá trị (tính tự động)

### Order
- `user`: User đặt hàng
- `product`: Sản phẩm đặt hàng
- `quantity`: Số lượng
- `total_amount`: Tổng tiền
- Thông tin giao hàng đầy đủ

## API Endpoints

### Product
- `GET /api/product/` - Lấy thông tin sản phẩm

### Cart
- `GET /api/cart/` - Lấy giỏ hàng của user
- `POST /api/cart/add_to_cart/` - Thêm sản phẩm vào giỏ hàng
- `POST /api/cart/update_quantity/` - Cập nhật số lượng
- `POST /api/cart/clear_cart/` - Xóa toàn bộ giỏ hàng

### Authentication
- `POST /api/auth/login/` - Đăng nhập
- `POST /api/auth/logout/` - Đăng xuất
- `POST /api/auth/signup/` - Đăng ký
- `GET /api/auth/me/` - Kiểm tra trạng thái đăng nhập

### Orders
- `GET /api/orders/` - Lấy danh sách đơn hàng
- `POST /api/orders/` - Tạo đơn hàng mới

## Cách sử dụng

### 1. Khởi động hệ thống

```bash
# Khởi động Docker containers
docker-compose up -d

# Tạo database và migrations
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate

# Tạo superuser
docker-compose exec backend python manage.py createsuperuser

# Tạo sản phẩm mẫu
docker-compose exec backend python manage.py shell -c "from store.models import SingleProduct; SingleProduct.objects.create(name='Magic Hummingbird Food Formula', description='The Best Hummingbird Food On Earth', price=20.00, currency='USD', is_active=True)"
```

### 2. Truy cập hệ thống

- **Backend Admin**: http://localhost:8000/admin/
- **API Health Check**: http://localhost:8000/health/
- **Frontend**: Mở file `cwish-fontend/nectar.html` trong trình duyệt
- **Test API**: Mở file `cwish-fontend/test-cart-api.html` để test các API

### 3. Sử dụng Cart

1. **Đăng nhập**: Sử dụng tài khoản đã tạo
2. **Thêm vào giỏ hàng**: Nhấn nút "Add to Cart" trên trang sản phẩm
3. **Điều chỉnh số lượng**: Sử dụng nút + và - trong mini-cart
4. **Xem giỏ hàng**: Mini-cart sẽ hiển thị thông tin sản phẩm và tổng tiền

## Cart Manager JavaScript

File `cart-manager.js` xử lý tất cả các thao tác liên quan đến giỏ hàng:

- `addToCart(quantity)`: Thêm sản phẩm vào giỏ hàng
- `updateCartQuantity(quantity)`: Cập nhật số lượng
- `clearCart()`: Xóa toàn bộ giỏ hàng
- `updateCartDisplay()`: Cập nhật giao diện giỏ hàng
- `updateMiniCartContent()`: Cập nhật nội dung mini-cart

## Tính năng đặc biệt

### Single Product Design
- Website chỉ bán duy nhất một sản phẩm
- Không cần chọn mẫu mã hay biến thể
- Tập trung vào việc điều chỉnh số lượng

### User-specific Cart
- Mỗi user có giỏ hàng riêng biệt
- Dữ liệu được lưu trữ theo user ID
- Bảo mật và riêng tư

### Real-time Updates
- Giỏ hàng cập nhật ngay lập tức khi có thay đổi
- Mini-cart hiển thị thông tin chính xác
- Tổng tiền được tính toán tự động

## Troubleshooting

### Lỗi thường gặp

1. **CORS Error**: Đảm bảo backend đang chạy trên localhost:8000
2. **Authentication Error**: Kiểm tra user đã đăng nhập chưa
3. **CSRF Token Error**: Kiểm tra cookie csrftoken có được set không

### Debug

- Sử dụng file `test-cart-api.html` để test từng API endpoint
- Kiểm tra console của trình duyệt để xem lỗi JavaScript
- Kiểm tra Django logs để xem lỗi backend

## Phát triển thêm

### Tính năng có thể thêm

- **Payment Integration**: Tích hợp thanh toán
- **Email Notifications**: Gửi email xác nhận đơn hàng
- **Inventory Management**: Quản lý tồn kho
- **Shipping Calculator**: Tính phí vận chuyển
- **Discount System**: Hệ thống giảm giá

### Cải tiến kỹ thuật

- **API Rate Limiting**: Giới hạn tần suất gọi API
- **Caching**: Cache dữ liệu sản phẩm
- **Logging**: Ghi log chi tiết
- **Testing**: Unit tests và integration tests
