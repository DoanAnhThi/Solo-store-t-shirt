from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
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
            order = serializer.save()
            response_serializer = OrderSerializer(order)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
