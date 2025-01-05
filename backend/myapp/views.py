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
# class InventoryDetail(APIView):
#     permission_classes = [IsAdmin]

#     def get_object(self, pk):
#         return get_object_or_404(Inventory, pk=pk)

#     def get(self, request, pk):
#         item = self.get_object(pk)
#         if request.user.role == 'admin' or request.user == item.user:
#             serializer = InventorySerializer(item)
#             return Response(serializer.data)
#         return Response({"error": "Unauthorized access."}, status=status.HTTP_403_FORBIDDEN)

#     def put(self, request, pk):
#         item = self.get_object(pk)
#         if request.user.role == 'admin' or request.user == item.user:
#             serializer = InventorySerializer(item, data=request.data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         return Response({"error": "Unauthorized access."}, status=status.HTTP_403_FORBIDDEN)

#     def delete(self, request, pk):
#         item = self.get_object(pk)
#         if request.user.role == 'admin' or request.user == item.user:
#             item.delete()
#             return Response({"message": "Inventory item deleted."}, status=status.HTTP_200_OK)
#         return Response({"error": "Unauthorized access."}, status=status.HTTP_403_FORBIDDEN)


# class SalesView(APIView):
#     permission_classes = [IsUserOrAdmin]

#     def get(self, request):
#         # Admins can view all sales
#         if request.user.role == 'admin':
#             sales = Sales.objects.all()
#         else:
#             # Users can view sales linked to their admin's inventory
#             if request.user.created_by:
#                 admin_inventory = Inventory.objects.filter(user=request.user.created_by)
#                 sales = Sales.objects.filter(product_sold__in=admin_inventory)
#             else:
#                 sales = Sales.objects.none()  # If no admin is linked, no sales are shown

#         serializer = SalesSerializer(sales, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         # Check if the user is linked to an admin
#         if request.user.role == 'user' and not request.user.created_by:
#             return Response(
#                 {"detail": "You do not have permission to make sales."},
#                 status=status.HTTP_403_FORBIDDEN,
#             )

#         # Ensure the product belongs to the admin's inventory and is shared with the user
#         serializer = SalesSerializer(data=request.data, context={'request': request})
#         if serializer.is_valid():
#             product_name = serializer.validated_data.get('product_name')  # Extract product_name from validated data
            
#             # Find the corresponding Inventory object based on product_name and the user's admin
#             try:
#                 product_instance = Inventory.objects.get(product=product_name, user=request.user.created_by)
#             except Inventory.DoesNotExist:
#                 return Response(
#                     {"detail": "Product does not exist in your admin's inventory."},
#                     status=status.HTTP_404_NOT_FOUND,
#                 )

#             # Save the sale and associate it with the user
#             sale = serializer.save(user=request.user, product_sold=product_instance)
#             return Response(SalesSerializer(sale).data, status=status.HTTP_201_CREATED)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
