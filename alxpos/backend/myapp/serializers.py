from .models import *
# from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth import authenticate

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "username", "email")


class UserRegistrationSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "password1", "password2")
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError("Passwords do not match!")

        password = attrs.get("password1", "")
        if len(password) < 8:
            raise serializers.ValidationError(
                "Passwords must be at least 8 characters!")

        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password1")
        validated_data.pop("password2")

        return CustomUser.objects.create_user(password=password, **validated_data)

class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials!")    

class InventorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Inventory
        fields = ['id', 'product', 'quantity', 'price']

class SalesSerializer(serializers.ModelSerializer):
    product_name = serializers.PrimaryKeyRelatedField(queryset=Inventory.objects.all(), write_only=True)  # Expecting product ID on input
    product_sold = serializers.CharField(source='product_sold.product', read_only=True)  # Display product name

    class Meta:
        model = Sales
        fields = ['id', 'product_sold', 'product_name', 'quantity_sold', 'selling_price', 'profit', 'sale_date']

    def create(self, validated_data):
        product_sold = validated_data.pop('product_name')  # Get the product instance using the product ID
        product_instance = Inventory.objects.get(id=product_sold.id)  # Get the actual product instance
        
        quantity_sold = validated_data['quantity_sold']

        # Check if enough inventory is available
        if product_instance.quantity < quantity_sold:
            raise serializers.ValidationError("Not enough stock to complete the sale")

        # Update inventory
        product_instance.quantity -= quantity_sold
        product_instance.save()  # Save the updated quantity in the inventory
        
        # Calculate profit
        total_cost = product_instance.price * quantity_sold
        total_selling_price = validated_data['selling_price'] * quantity_sold
        profit = total_selling_price - total_cost

        # Create sale record
        sale = Sales.objects.create(product_sold=product_instance, profit=profit, **validated_data)
        return sale

# class SalesSerializer(serializers.ModelSerializer):
#     product_name = serializers.PrimaryKeyRelatedField(queryset=Inventory.objects.all(), write_only=True)  # Expecting product ID on input
#     product_sold = serializers.CharField(source='product_sold.product', read_only=True)  # Display product name

#     class Meta:
#         model = Sales
#         fields = ['id', 'product_sold', 'product_name', 'quantity_sold', 'selling_price', 'profit', 'sale_date']
            
#     def create(self, validated_data):
#         product_sold = validated_data.pop('product_sold')  # Extract the product sold
#         quantity_sold = validated_data['quantity_sold']
        
#         # Check if enough inventory is available
#         if product_sold.quantity < quantity_sold:
#             raise serializers.ValidationError("Not enough stock to complete the sale")

#         # Update inventory
#         product_sold.quantity -= quantity_sold
#         product_sold.save()  # Save the updated quantity in the inventory
        
#         # Calculate profit
#         total_cost = product_sold.price * quantity_sold
#         total_selling_price = validated_data['selling_price'] * quantity_sold
#         profit = total_selling_price - total_cost

#         # Create sale record
#         sale = Sales.objects.create(product_sold=product_sold, profit=profit, **validated_data)
#         return sale




