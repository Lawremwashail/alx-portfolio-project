from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import *
from rest_framework.permissions import IsAdminUser
from .serializers import *
from .decorators import IsAdmin, IsUserOrAdmin
from rest_framework.permissions import IsAdminUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.shortcuts import get_object_or_404
from django.core.cache import cache

# Custom Token Serializer
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['role'] = user.role
        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

# User Registration View
class UserRegistrationAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = RefreshToken.for_user(user)
        data = serializer.data
        data["tokens"] = {"refresh": str(token), "access": str(token.access_token)}
        return Response(data, status=status.HTTP_201_CREATED)

# User Login View
class UserLoginAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        token = RefreshToken.for_user(user)
        data = CustomUserSerializer(user).data
        data["tokens"] = {"refresh": str(token), "access": str(token.access_token)}
        return Response(data, status=status.HTTP_200_OK)

# Admin Add User View
class AdminAddUserAPIView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save(created_by=request.user)
            return Response(
                {
                    "message": "User created successfully.",
                    "user": {
                        "username": user.username,
                        "email": user.email,
                        "role": user.role,
                    }
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# User Logout View
class UserLogoutAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"error": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)

# User Info View
class UserInfoAPIView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomUserSerializer

    def get(self, request):
        user_data = {
            "username": request.user.username,
            "email": request.user.email,
        }
        return Response(user_data)

# Inventory Views
class InventoryItems(APIView):
    permission_classes = [IsUserOrAdmin]

    def get(self, request):
        cache_key = f"inventory_{request.user.id}_{request.user.role}"
        cached_inventory = cache.get(cache_key)

        if cached_inventory is not None:
            return Response(cached_inventory)
        
        if request.user.role == 'admin':
            inventory = Inventory.objects.filter(created_by=request.user)
        else:
            inventory = Inventory.objects.filter(created_by=request.user.created_by)
        

        if not inventory:
            return Response({"message": "No items found."}, status=status.HTTP_200_OK)
        
        class ProductNameSerializer(serializers.ModelSerializer):
            class Meta:
                model = Inventory
                fields = ['id', 'product', 'quantity', 'price'] 

        serializer = ProductNameSerializer(inventory, many=True)
        
        cache.set(cache_key, serializer.data, timeout=3600)
        return Response(serializer.data)

    def post(self, request):
        # Admin-only post to add inventory items
        if request.user.role != 'admin':
            return Response({'detail': 'Only admins can add inventory.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = InventorySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            
            cache_key = f"inventory_{request.user.id}_{request.user.role}"
            cache.delete(cache_key)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InventoryDetail(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, pk):
        item = get_object_or_404(Inventory, pk=pk)
        serializer = InventorySerializer(item)
        return Response(serializer.data)

    def put(self, request, pk):
        item = get_object_or_404(Inventory, pk=pk)
        serializer = InventorySerializer(item, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()

            cache_key = f"inventory_{request.user.id}_{request.user.role}"
            cache.delete(cache_key)

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        item = get_object_or_404(Inventory, pk=pk)
        item.delete()

        cache_key = f"inventory_{request.user.id}_{request.user.role}"
        cache.delete(cache_key)

        return Response({"message": "Item deleted."}, status=status.HTTP_200_OK)

class SalesListCreateView(APIView):
    permission_classes = [IsUserOrAdmin]

    def get(self, request):

        cached_key = f"sales_{request.user.id}_{request.user.role}"
        cached_sales = cache.get(cached_key)

        if cached_sales is not None:
            return Response(cached_sales)
        
        if request.user.role == 'admin':
            # Admins see all sales related to their inventory, including their own and sales by users they created
            sales = Sales.objects.filter(product_sold__created_by=request.user)
        else:
            # Users see only their own sales
            sales = Sales.objects.filter(created_by=request.user)

        serializer = SalesSerializer(sales, many=True, context={'request': request})
        cache.set(cached_key, serializer.data, timeout=3600)

        return Response(serializer.data)

    def post(self, request):
        serializer = SalesSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            product_name = request.data.get('product_name')
            product = Inventory.objects.filter(product=product_name).first()

            if not product:
                return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)


            if request.user.role == 'user':
                if product.created_by != request.user.created_by:
                    return Response({"error": "You are not authorized to sell this product."}, status=status.HTTP_403_FORBIDDEN)

            if request.user.role == 'admin' and product.created_by != request.user:
                return Response({"error": "You are not authorized to sell this product."}, status=status.HTTP_403_FORBIDDEN)

            
            # Save the sale
            serializer.save(created_by=request.user)
            
            cache_key = f"sales_{request.user.id}_{request.user.role}"
            cache.delete(cache_key)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SalesDetailView(APIView):
    permission_classes = [IsUserOrAdmin]

    def get(self, request, pk):

        cache_key = f"sales_{pk}_{request.user.id}_{request.user.role}"
        cached_sale = cache.get(cache_key) 

        if cached_sale is not None:
            return Response(cached_sale)
        
        sale = get_object_or_404(Sales, pk=pk)

        # Users can only view their own sales
        if request.user.role == 'user' and sale.created_by != request.user:
            return Response({"error": "You do not have permission to access this sale."}, status=status.HTTP_403_FORBIDDEN)

        # Admins can only view sales related to their inventory
        if request.user.role == 'admin' and sale.product_sold.created_by != request.user:
            return Response({"error": "You do not have permission to view this sale."}, status=status.HTTP_403_FORBIDDEN)

        serializer = SalesSerializer(sale, context={'request': request})
        cache.set(cache_key, serializer.data, timeout=3600)

        return Response(serializer.data)

    def put(self, request, pk):
        # PUT is restricted to admins only
        if request.user.role != 'admin':
            return Response({"error": "Only admins can modify sales."}, status=status.HTTP_403_FORBIDDEN)

        sale = get_object_or_404(Sales, pk=pk)

        # Admins can only modify sales related to their inventory
        if sale.product_sold.created_by != request.user:
            return Response({"error": "You do not have permission to modify this sale."}, status=status.HTTP_403_FORBIDDEN)

        serializer = SalesSerializer(sale, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            
            cache_key = f"sale_{pk}_{request.user.id}_{request.user.role}"
            cache.delete(cache_key)

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        # DELETE is restricted to admins only
        if request.user.role != 'admin':
            return Response({"error": "Only admins can delete sales."}, status=status.HTTP_403_FORBIDDEN)

        sale = get_object_or_404(Sales, pk=pk)

        # Admins can only delete sales related to their inventory
        if sale.product_sold.created_by != request.user:
            return Response({"error": "You do not have permission to delete this sale."}, status=status.HTTP_403_FORBIDDEN)

        sale.delete()
        cache_key = f"sale_{pk}_{request.user.id}_{request.user.role}"
        cache.delete(cache_key)
        
        return Response({"message": "Sale deleted."}, status=status.HTTP_200_OK)
