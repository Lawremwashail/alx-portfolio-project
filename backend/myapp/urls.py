from rest_framework_simplejwt.views import TokenRefreshView
# from .views import AdminAddUserAPIView
from django.urls import path
from . import views

app_name = 'myappp'
urlpatterns = [
    path("register/", views.UserRegistrationAPIView.as_view(), name="register-user"),
    path("login/", views.UserLoginAPIView.as_view(), name="login-user"),
    path("logout/", views.UserLogoutAPIView.as_view(), name="logout-user"),
    path("token/", views.MyTokenObtainPairView.as_view(), name="token-obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("user/", views.UserInfoAPIView.as_view(), name="user-info"),
    path('inventory/', views.InventoryItems.as_view(), name='inventory_items'),
    path('inventory/<int:pk>/', views.InventoryDetail.as_view(), name='inventory_detail'),
    path('sales/', views.SalesListCreateView.as_view(), name='sales-list-create'),  # Ensure this URL pattern is added
    path('sales/<int:pk>/', views.SalesDetailView.as_view(), name='sales-detail'),  # Ensure this URL pattern is added
]