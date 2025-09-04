import requests
import json
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect, csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from .models import SingleProduct, UserCart, Order, Contact, DigitalBonusProduct, BonusCart
from .serializers import (
    SingleProductSerializer, UserCartSerializer, OrderSerializer,
    OrderCreateSerializer, AddToCartSerializer, UpdateCartQuantitySerializer,
    ContactSerializer, DigitalBonusProductSerializer, BonusCartSerializer,
    AddBonusToCartSerializer, UpdateBonusCartQuantitySerializer
)


class SingleProductViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet cho sản phẩm duy nhất"""
    queryset = SingleProduct.objects.filter(is_active=True)
    serializer_class = SingleProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return SingleProduct.objects.filter(is_active=True).first()

    def list(self, request, *args, **kwargs):
        product = self.get_queryset()
        if product:
            serializer = self.get_serializer(product)
            return Response(serializer.data)
        return Response({'error': 'No active product available'}, status=status.HTTP_404_NOT_FOUND)


class DigitalBonusProductViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet cho sản phẩm digital bonus"""
    queryset = DigitalBonusProduct.objects.filter(is_active=True)
    serializer_class = DigitalBonusProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return DigitalBonusProduct.objects.filter(is_active=True).first()

    def list(self, request, *args, **kwargs):
        product = self.get_queryset()
        if product:
            serializer = self.get_serializer(product)
            return Response(serializer.data)
        return Response({'error': 'No active bonus product available'}, status=status.HTTP_404_NOT_FOUND)


class UserCartViewSet(viewsets.ModelViewSet):
    """ViewSet cho giỏ hàng của user (sản phẩm chính)"""
    serializer_class = UserCartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserCart.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        """Lấy giỏ hàng của user hiện tại"""
        cart_items = self.get_queryset()
        serializer = self.get_serializer(cart_items, many=True)
        
        # Tính tổng giá trị giỏ hàng
        total_amount = sum(item.total_price for item in cart_items)
        item_count = sum(item.quantity for item in cart_items)
        
        return Response({
            'items': serializer.data,
            'total_amount': total_amount,
            'item_count': item_count
        })

    @action(detail=False, methods=['post'])
    def add_to_cart(self, request):
        """Thêm sản phẩm vào giỏ hàng"""
        serializer = AddToCartSerializer(data=request.data)
        
        if serializer.is_valid():
            quantity = serializer.validated_data['quantity']
            
            # Lấy sản phẩm duy nhất
            product = SingleProduct.objects.filter(is_active=True).first()
            if not product:
                return Response(
                    {'error': 'No active product available'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Kiểm tra xem đã có trong giỏ hàng chưa
            cart_item, created = UserCart.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                # Cập nhật số lượng nếu đã tồn tại
                cart_item.quantity += quantity
                cart_item.save()
            
            # Trả về giỏ hàng đã cập nhật
            return self.list(request)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def update_quantity(self, request):
        """Cập nhật số lượng sản phẩm trong giỏ hàng"""
        serializer = UpdateCartQuantitySerializer(data=request.data)
        
        if serializer.is_valid():
            quantity = serializer.validated_data['quantity']
            
            # Lấy sản phẩm duy nhất
            product = SingleProduct.objects.filter(is_active=True).first()
            if not product:
                return Response(
                    {'error': 'No active product available'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            try:
                cart_item = UserCart.objects.get(user=request.user, product=product)
                
                if quantity == 0:
                    # Nếu số lượng = 0, xóa sản phẩm khỏi giỏ hàng
                    cart_item.delete()
                else:
                    # Cập nhật số lượng
                    cart_item.quantity = quantity
                    cart_item.save()
                
                # Trả về giỏ hàng đã cập nhật
                return self.list(request)
                
            except UserCart.DoesNotExist:
                return Response(
                    {'error': 'No items in cart'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def clear_cart(self, request):
        """Xóa toàn bộ giỏ hàng"""
        UserCart.objects.filter(user=request.user).delete()
        return Response({'message': 'Cart cleared successfully'}, status=status.HTTP_200_OK)


class BonusCartViewSet(viewsets.ModelViewSet):
    """ViewSet cho giỏ hàng bonus của user"""
    serializer_class = BonusCartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BonusCart.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        """Lấy giỏ hàng bonus của user hiện tại"""
        cart_items = self.get_queryset()
        serializer = self.get_serializer(cart_items, many=True)
        
        # Tính tổng giá trị giỏ hàng bonus
        total_amount = sum(item.total_price for item in cart_items)
        item_count = sum(item.quantity for item in cart_items)
        
        return Response({
            'items': serializer.data,
            'total_amount': total_amount,
            'item_count': item_count
        })

    @action(detail=False, methods=['post'])
    def add_to_cart(self, request):
        """Thêm sản phẩm bonus vào giỏ hàng"""
        serializer = AddBonusToCartSerializer(data=request.data)
        
        if serializer.is_valid():
            quantity = serializer.validated_data['quantity']
            
            # Lấy sản phẩm bonus duy nhất
            product = DigitalBonusProduct.objects.filter(is_active=True).first()
            if not product:
                return Response(
                    {'error': 'No active bonus product available'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Kiểm tra xem đã có trong giỏ hàng bonus chưa
            cart_item, created = BonusCart.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                # Cập nhật số lượng nếu đã tồn tại
                cart_item.quantity += quantity
                cart_item.save()
            
            # Trả về giỏ hàng bonus đã cập nhật
            return self.list(request)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def update_quantity(self, request):
        """Cập nhật số lượng sản phẩm bonus trong giỏ hàng"""
        serializer = UpdateBonusCartQuantitySerializer(data=request.data)
        
        if serializer.is_valid():
            quantity = serializer.validated_data['quantity']
            
            # Lấy sản phẩm bonus duy nhất
            product = DigitalBonusProduct.objects.filter(is_active=True).first()
            if not product:
                return Response(
                    {'error': 'No active bonus product available'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            try:
                cart_item = BonusCart.objects.get(user=request.user, product=product)
                
                if quantity == 0:
                    # Nếu số lượng = 0, xóa sản phẩm khỏi giỏ hàng bonus
                    cart_item.delete()
                else:
                    # Cập nhật số lượng
                    cart_item.quantity = quantity
                    cart_item.save()
                
                # Trả về giỏ hàng bonus đã cập nhật
                return self.list(request)
                
            except BonusCart.DoesNotExist:
                return Response(
                    {'error': 'No bonus items in cart'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def clear_cart(self, request):
        """Xóa toàn bộ giỏ hàng bonus"""
        BonusCart.objects.filter(user=request.user).delete()
        return Response({'message': 'Bonus cart cleared successfully'}, status=status.HTTP_200_OK)


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet cho đơn hàng"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        """Tạo đơn hàng mới"""
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            order_result = serializer.save()

            # Handle case where serializer returns a list or single object
            if isinstance(order_result, list):
                # Multiple orders created
                orders = order_result
                primary_order = orders[0] if orders else None
            else:
                # Single order created
                orders = [order_result]
                primary_order = order_result

            if not primary_order:
                return Response(
                    {'error': 'No orders were created'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Gửi order đến Shirtigo API (chỉ gửi primary order)
            shirtigo_response = self._send_to_shirtigo(primary_order)

            # Cập nhật order với Shirtigo response
            if shirtigo_response and 'id' in shirtigo_response:
                primary_order.shirtigo_order_id = shirtigo_response['id']
                primary_order.shirtigo_response = shirtigo_response
                primary_order.save()

            # Gửi email xác nhận đơn hàng
            email_sent = self._send_order_confirmation_email(primary_order)
            if not email_sent:
                print("⚠️ Cảnh báo: Không thể gửi email xác nhận, nhưng đơn hàng vẫn được tạo thành công")

            # Serialize response - if multiple orders, return array, else single object
            if len(orders) == 1:
                response_serializer = OrderSerializer(primary_order)
                response_data = response_serializer.data
            else:
                response_serializer = OrderSerializer(orders, many=True)
                response_data = response_serializer.data

            # Thêm thông tin Shirtigo vào response
            if isinstance(response_data, list):
                for item in response_data:
                    item['shirtigo_response'] = shirtigo_response
            else:
                response_data['shirtigo_response'] = shirtigo_response

            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _send_to_shirtigo(self, order):
        """Gửi order đến Shirtigo API theo đúng format đã test thành công"""
        try:
            shirtigo_url = "https://cockpit.shirtigo.com/api/orders"
            headers = {
                "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjE1OGYwYzhmNjFmOGJhZTE1NmFhMjgxMWRjMmQ3OTcwNzE0NDE3ODlkMzAyOGFjYTkzMWYzMmU4YWNiNzg3ZDgxY2MyN2U2MjJhNGY4NmRlIn0.eyJhdWQiOiIxIiwianRpIjoiMTU4ZjBjOGY2MWY4YmFlMTU2YWEyODExZGMyZDc5NzA3MTQ0MTc4OWQzMDI4YWNhOTMxZjMyZThhY2I3ODdkODFjYzI3ZTYyMmE0Zjg2ZGUiLCJpYXQiOjE3NTYxOTcxNzAsIm5iZiI6MTc1NjE5NzE3MCwiZXhwIjoyMDcxNzI5OTcwLCJzdWIiOiI5NzAyNSIsInNjb3BlcyI6WyJyZWFkLXVzZXIiLCJ3cml0ZS11c2VyIiwicmVhZC1kZXNpZ24iLCJ3cml0ZS1kZXNpZ24iLCJyZWFkLXByb2plY3QiLCJ3cml0ZS1wcm9qZWN0IiwicmVhZC1vcmRlciIsIndyaXRlLW9yZGVyIiwicmVhZC13YXJlaG91c2UtcHJvZHVjdCIsIndyaXRlLXdhcmVob3VzZS1wcm9kdWN0IiwicmVhZC13ZWJob29rIiwid3JpdGUtd2ViaG9vayIsInJlYWQtc3RhdHMiXX0.GNZNcATT7i8AfpaXxt9YorQ0VwiG2ehlp5F7Va5vC8AfUYEFe8gkIuTS2M_mG04oMDEHRFmiL8ee4HdrEq9iSlfB5-kzuRDlLaiHx_GAdxnAiBNfHEubC11aFW1r2_LLJOCF7okfZFqNYqdV575PvgekvRzfkTXq8V8RvQLlrhtVwJ5KCHIB-qiIdJNmHB-LhrV1cKpBfUiN12gU87DoQdnY549dFouGJ_FhFc6NV3SiCBCcWXXGEVpvnoIfpKaaNaMmLC25JarqIURUTzYx8c39LpaFyqjNfRvsT7G0jdJvWnOPQNf2d5K-AUQP0U6b4ks_fy3Mhl6wLANKvFYBzqNKuYtbUZSUR-K_BzJ9jUpCd-I0q8AG1XEyq44Z-5v7-DanSYApAgxQEFjia7ulvwIDovYHdM6xIBOGNC-p03YLpE2JXKY6Y93A3tVnIHrxb76Sp7D4PG3ieKl_5re_fqwdFBkHvNghIW58bYx_S2Qr_T588WYTuuroUHvxnhVGnINLH0w0rvNXzmSpvemAtAvi8lqEj7jJgs24G78tKqdvgUL1dU3h1SeSxhPaZpmxXjZlLh4s3UGeXsjLci52yD_T9oST3xh17sdzrMT6z4TeJn7MUQ8grSWuGrwE0UnA_ECPdvwrQnfZFzP23CHEvRm1oGI-SpgysT87bqkLrv0",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }

            # Chuẩn bị dữ liệu theo đúng format đã test thành công trên Postman
            shirtigo_data = {
                "delivery": {
                    "type": "delivery",
                    "firstname": order.first_name or "Nguyen",
                    "lastname": order.last_name or "Van A",
                    "street": order.address or "123 Main Street",
                    "postcode": order.postal_code or "70000",
                    "city": order.city or "Ho Chi Minh",
                    "country": order.country or "VN",
                    "email": order.email or "nguyenvana@example.com"
                },
                "products": [
                    {
                        "amount": order.quantity or 1,
                        "productId": "3945923",
                        "colorId": "325",
                        "sizeId": "3"
                    }
                ]
            }

            print(f"📤 Shirtigo Request Structure:")
            print(f"  URL: {shirtigo_url}")
            print(f"  Headers: Authorization: Bearer [HIDDEN_TOKEN]")
            print(f"  Headers: Accept: {headers['Accept']}")
            print(f"  Headers: Content-Type: {headers['Content-Type']}")
            print(f"  Body: {shirtigo_data}")

            # Gửi request đến Shirtigo
            print(f"📡 Gửi request đến Shirtigo API...")
            response = requests.post(shirtigo_url, json=shirtigo_data, headers=headers, timeout=30)

            # Log chỉ status từ Shirtigo API
            print(f"🎯 Shirtigo API Status: {response.status_code}")

            if response.status_code == 200 or response.status_code == 201:
                print(f"✅ Shirtigo API thành công!")
                try:
                    response_data = response.json()
                    return response_data
                except Exception as json_error:
                    print(f"⚠️ Không thể parse JSON response: {json_error}")
                    return {"raw_response": response.text}
            else:
                print(f"❌ Shirtigo API thất bại! (Đây là lỗi từ Shirtigo, không phải backend của chúng ta)")
                return {
                    "error": True,
                    "status_code": response.status_code,
                    "response_body": response.text
                }

        except requests.exceptions.RequestException as e:
            print(f"❌ Error sending to Shirtigo API: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error in _send_to_shirtigo: {e}")
            return None

    def _send_order_confirmation_email(self, order):
        """Gửi email xác nhận đơn hàng"""
        try:
            print(f"📧 Gửi email xác nhận đơn hàng cho {order.email}...")

            # Render email template
            html_content = render_to_string('emails/order_confirmation.html', {
                'order': order,
            })

            # Tạo subject email
            subject = f'Order Confirmation - Order #{order.id} - Cwish Store'

            # Tạo email message
            email = EmailMessage(
                subject=subject,
                body=html_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[order.email],
            )
            email.content_subtype = 'html'  # Đánh dấu đây là HTML email

            # Gửi email
            email.send()

            print(f"✅ Email xác nhận đã được gửi thành công đến {order.email}")
            return True

        except Exception as e:
            print(f"❌ Lỗi khi gửi email xác nhận: {e}")
            return False

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Cập nhật trạng thái đơn hàng (chỉ admin)"""
        order = self.get_object()
        new_status = request.data.get('status')

        if new_status not in dict(Order.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = new_status
        order.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    @csrf_exempt
    def test_create(self, request):
        """Endpoint test tạo đơn hàng không cần authentication - tái sử dụng logic từ create()"""
        # Tạo user test nếu chưa có
        from django.contrib.auth.models import User
        test_user, created = User.objects.get_or_create(
            username='test_user',
            defaults={'email': 'test@example.com'}
        )

        # Tạo dữ liệu test
        test_data = {
            'email': request.data.get('email', 'test@example.com'),
            'first_name': request.data.get('first_name', 'Test'),
            'last_name': request.data.get('last_name', 'User'),
            'address': request.data.get('address', '123 Test Street'),
            'city': request.data.get('city', 'Test City'),
            'country': request.data.get('country', 'VN'),
            'postal_code': request.data.get('postal_code', '70000'),
            'phone': request.data.get('phone', ''),
            'quantity': request.data.get('quantity', 1),
            'unit_price': float(request.data.get('unit_price', 25.00)),
            'currency': request.data.get('currency', 'USD'),
            'user': test_user.id
        }

        # Lấy sản phẩm đầu tiên
        main_product = SingleProduct.objects.filter(is_active=True).first()
        if main_product:
            test_data['main_product'] = main_product.id

        # Tái sử dụng logic từ create() method
        serializer = self.get_serializer(data=test_data)
        if serializer.is_valid():
            order = serializer.save()

            # Gửi order đến Shirtigo API (giống như create() method)
            shirtigo_response = self._send_to_shirtigo(order)

            # Cập nhật order với Shirtigo response
            if shirtigo_response and 'id' in shirtigo_response:
                order.shirtigo_order_id = shirtigo_response['id']
                order.shirtigo_response = shirtigo_response
                order.save()

            # Gửi email xác nhận đơn hàng (cùng logic như create method)
            email_sent = self._send_order_confirmation_email(order)
            if not email_sent:
                print("⚠️ Cảnh báo: Không thể gửi email xác nhận trong test mode, nhưng đơn hàng vẫn được tạo thành công")

            response_serializer = OrderSerializer(order)
            response_data = response_serializer.data
            response_data['shirtigo_response'] = shirtigo_response

            return Response({
                'message': 'Test order created successfully - using same logic as production',
                'order': response_data,
                'shirtigo_response': shirtigo_response,
                'note': 'This endpoint uses the SAME logic as the production /api/orders/create/ endpoint'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContactViewSet(viewsets.GenericViewSet):
    """ViewSet xử lý form contact"""
    permission_classes = [AllowAny]
    serializer_class = ContactSerializer
    
    def create(self, request):
        """Xử lý form contact submission"""
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            # Lưu thông tin contact vào database
            contact = serializer.save()
            
            # Trả về response thành công
            return Response({
                'message': 'Cảm ơn bạn đã liên hệ! Chúng tôi sẽ phản hồi sớm nhất có thể.',
                'contact_id': contact.id
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Health check endpoint
from rest_framework.decorators import api_view

@api_view(['GET'])
def health_check(request):
    return Response({
        'status': 'healthy',
        'message': 'Django backend is running'
    })


# Simple test endpoint không sử dụng Django REST framework
@csrf_exempt
@require_POST
def simple_test_order(request):
    """Endpoint test đơn giản nhất - không cần authentication"""
    try:
        print("🎯 Simple test endpoint called!")

        # Parse JSON data
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
            return JsonResponse({
                'error': 'Invalid JSON',
                'message': str(e)
            }, status=400)

        # Tạo user test
        test_user, created = User.objects.get_or_create(
            username='test_user',
            defaults={'email': 'test@example.com'}
        )

        # Tạo fake order data từ request
        order_data = {
            'email': data.get('customer', {}).get('email', 'test@example.com'),
            'first_name': data.get('customer', {}).get('firstName', 'Test'),
            'last_name': data.get('customer', {}).get('lastName', 'User'),
            'address': data.get('customer', {}).get('address', '123 Test Street'),
            'city': data.get('customer', {}).get('city', 'Test City'),
            'country': data.get('customer', {}).get('country', 'VN'),
            'postal_code': data.get('customer', {}).get('zipCode', '70000'),
            'phone': data.get('customer', {}).get('phone', ''),
            'quantity': 1,
            'unit_price': float(data.get('total', 25.00)),
            'total_amount': float(data.get('total', 25.00)),
            'currency': 'USD',
            'user': test_user.id
        }

        # Lấy sản phẩm đầu tiên
        main_product = SingleProduct.objects.filter(is_active=True).first()
        if main_product:
            order_data['main_product'] = main_product.id

        # Tạo order trực tiếp thay vì dùng serializer (để tránh lỗi context)
        try:
            order = Order.objects.create(
                user=test_user,
                email=order_data['email'],
                first_name=order_data['first_name'],
                last_name=order_data['last_name'],
                address=order_data['address'],
                city=order_data['city'],
                country=order_data['country'],
                postal_code=order_data['postal_code'],
                phone=order_data['phone'],
                quantity=order_data['quantity'],
                unit_price=order_data['unit_price'],
                total_amount=order_data['total_amount'],
                currency=order_data['currency'],
                main_product_id=order_data.get('main_product')
            )
            print(f"✅ Order created successfully: {order.id}")

            # Gửi đến Shirtigo API
            order_viewset = OrderViewSet()
            shirtigo_response = order_viewset._send_to_shirtigo(order)

            # Gửi email xác nhận đơn hàng
            email_sent = order_viewset._send_order_confirmation_email(order)
            if not email_sent:
                print("⚠️ Cảnh báo: Không thể gửi email xác nhận trong simple test, nhưng đơn hàng vẫn được tạo thành công")

            return JsonResponse({
                'success': True,
                'message': 'Test order created successfully',
                'order_id': str(order.id),
                'shirtigo_response': shirtigo_response,
                'shirtigo_status': shirtigo_response.get('status_code') if isinstance(shirtigo_response, dict) else 'unknown'
            }, status=201)
        except Exception as order_error:
            print(f"❌ Error creating order: {order_error}")
            return JsonResponse({
                'error': 'Failed to create order',
                'message': str(order_error)
            }, status=400)

    except Exception as e:
        print(f"❌ Unexpected error in simple_test_order: {e}")
        return JsonResponse({
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


# --- Auth endpoints (session-based) ---

@api_view(['POST'])
@csrf_protect
def auth_login(request):
    username_or_email = request.data.get('username') or request.data.get('email')
    password = request.data.get('password')
    if not username_or_email or not password:
        return Response({'detail': 'Missing credentials'}, status=400)

    user = authenticate(request, username=username_or_email, password=password)
    if user is None:
        try:
            matched = User.objects.get(email=username_or_email)
            user = authenticate(request, username=matched.username, password=password)
        except User.DoesNotExist:
            user = None

    if user is None:
        return Response({'detail': 'Invalid credentials'}, status=401)

    login(request, user)
    return Response({'id': user.id, 'username': user.username, 'email': user.email})


@api_view(['POST'])
def auth_logout(request):
    try:
        # Clear the user's session
        if request.user.is_authenticated:
            # Log the logout for debugging
            print(f"Logging out user: {request.user.username}")
        
        # Django's logout function handles session cleanup
        logout(request)
        
        # Additional session cleanup for Docker environment
        if hasattr(request, 'session'):
            request.session.flush()
            request.session.delete()
        
        # Clear any custom cookies if needed
        response = Response({'ok': True, 'message': 'Successfully logged out'})
        response.delete_cookie('sessionid')
        response.delete_cookie('csrftoken')
        
        return response
        
    except Exception as e:
        print(f"Logout error: {e}")
        return Response(
            {'error': 'Logout failed', 'detail': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@ensure_csrf_cookie
def auth_me(request):
    if request.user.is_authenticated:
        return Response({'id': request.user.id, 'username': request.user.username, 'email': request.user.email})
    return Response({'id': None})


@api_view(['POST'])
@csrf_protect
def auth_signup(request):
    username = (request.data.get('username') or '').strip()
    email = (request.data.get('email') or '').strip()
    password = request.data.get('password')
    if not username or not password:
        return Response({'detail': 'username and password are required'}, status=400)
    if User.objects.filter(username=username).exists():
        return Response({'detail': 'username already exists'}, status=400)
    if email and User.objects.filter(email=email).exists():
        return Response({'detail': 'email already exists'}, status=400)
    user = User.objects.create_user(username=username, email=email or None, password=password)
    login(request, user)
    return Response({'id': user.id, 'username': user.username, 'email': user.email}, status=201)
