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
    permission_classes = [IsAdminUser]

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
    permission_classes = [IsAdmin]

    def get(self, request):
        inventory = Inventory.objects.all()
        serializer = InventorySerializer(inventory, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = InventorySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InventoryDetail(APIView):
    permission_classes = [IsAdmin]  # Only admins can modify inventory

    def get(self, request, pk):
        try:
            item = Inventory.objects.get(pk=pk)
        except Inventory.DoesNotExist:
            return Response({"error": "Item not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = InventorySerializer(item)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            item = Inventory.objects.get(pk=pk)
        except Inventory.DoesNotExist:
            return Response({"error": "Item not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = InventorySerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            item = Inventory.objects.get(pk=pk)
        except Inventory.DoesNotExist:
            return Response({"error": "Item not found."}, status=status.HTTP_404_NOT_FOUND)
        
        item.delete()
        return Response({"message": "Item deleted."}, status=status.HTTP_200_OK)


class SalesListCreateView(APIView):
    permission_classes = [IsUserOrAdmin]  # Admins and Users can access

    def get(self, request):
        if request.user.role == 'admin':
            sales = Sales.objects.all()
        else:
            sales = Sales.objects.filter(user=request.user.created_by)

        serializer = SalesSerializer(sales, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SalesSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(admin=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SalesDetailView(APIView):
    permission_classes = [IsUserOrAdmin]  # Admins and Users can access

    def get_object(self, pk):
        try:
            return Sales.objects.get(pk=pk)
        except Sales.DoesNotExist:
            return None

    def get(self, request, pk):
        sale = self.get_object(pk)
        if sale is None:
            return Response({"error": "Sale not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the user has permission to access this sale
        if request.user.role == 'user' and sale.admin != request.user.created_by:
            return Response({"error": "You do not have permission to access this sale."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = SalesSerializer(sale)
        return Response(serializer.data)

    def put(self, request, pk):
        sale = self.get_object(pk)
        if sale is None:
            return Response({"error": "Sale not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.user.role == 'user' and sale.admin != request.user.created_by:
            return Response({"error": "You do not have permission to modify this sale."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = SalesSerializer(sale, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        sale = self.get_object(pk)
        if sale is None:
            return Response({"error": "Sale not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.user.role == 'user' and sale.admin != request.user.created_by:
            return Response({"error": "You do not have permission to delete this sale."}, status=status.HTTP_403_FORBIDDEN)

        sale.delete()
        return Response({"message": "Sale deleted."}, status=status.HTTP_200_OK)