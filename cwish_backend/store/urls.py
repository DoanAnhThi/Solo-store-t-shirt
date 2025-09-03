from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'product', views.SingleProductViewSet, basename='product')
router.register(r'bonus-product', views.DigitalBonusProductViewSet, basename='bonus-product')
router.register(r'cart', views.UserCartViewSet, basename='cart')
router.register(r'bonus-cart', views.BonusCartViewSet, basename='bonus-cart')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'contact', views.ContactViewSet, basename='contact')

urlpatterns = [
    path('api/', include(router.urls)),
    path('health/', views.health_check, name='health_check'),
    # Auth endpoints
    path('api/auth/login/', views.auth_login, name='auth_login'),
    path('api/auth/logout/', views.auth_logout, name='auth_logout'),
    path('api/auth/me/', views.auth_me, name='auth_me'),
    path('api/auth/signup/', views.auth_signup, name='auth_signup'),
]
