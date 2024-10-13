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
    product_name = serializers.CharField(source='product.product', read_only=True)  # Include the product name
    product = serializers.PrimaryKeyRelatedField(queryset=Inventory.objects.all())
    
    class Meta:
        model = Sales
        fields = ['product','product_name', 'quantity_sold', 'selling_price', 'profit', 'sale_date']

        
    def create(self, validated_data):
        product = validated_data['product']
        quantity_sold = validated_data['quantity_sold']
        selling_price = validated_data['selling_price']

        try:
            inventory_item = Inventory.objects.get(product=product)
            if inventory_item.quantity < quantity_sold:
                raise serializers.ValidationError('Not enough inventory')

            # Update inventory
            inventory_item.quantity -= quantity_sold
            inventory_item.save()

            # Calculate profit
            cost_price = inventory_item.price
            total_cost = cost_price * quantity_sold
            total_revenue = selling_price * quantity_sold
            profit = total_revenue - total_cost

            # Create sale record
            sale = Sales.objects.create(
                product=inventory_item,
                quantity_sold=quantity_sold,
                selling_price=selling_price,
                profit=profit
            )
            return sale
        except Inventory.DoesNotExist:
            raise serializers.ValidationError('Product not found')
