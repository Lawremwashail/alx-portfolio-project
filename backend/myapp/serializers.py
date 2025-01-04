from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'created_by']

        def create(self, validated_data):
            request = self.context.get('request')
            if request and request.user.is_authenticated:
                validated_data['created_by'] = request.user
            return super().create(validated_data)

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2', 'role']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords must match"})
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        created_by = request.user if request and request.user.is_authenticated else None
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email'],
            role=validated_data['role'],
            created_by=created_by
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        user = get_user_model().objects.filter(email=attrs['email']).first()
        if user and user.check_password(attrs['password']):
            return user
        raise serializers.ValidationError("Invalid email or password")

class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ['id', 'user', 'product', 'quantity', 'price']

class SalesSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_sold.product')
    class Meta:
        model = Sales
        fields = ['id', 'product_sold', 'quantity_sold', 'selling_price', 'profit', 'sale_date', 'user', 'product_name']

    def create(self, validated_data):
        sale = Sales(**validated_data)
        sale.save()
        return sale


class SalesSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())  # Set the user making the sale (read-only)
    product_name = serializers.CharField(write_only=True)  # Expecting product name as input
    product_sold = serializers.CharField(source='product_sold.product', read_only=True)  # Display product name (read-only)
    
    class Meta:
        model = Sales
        fields = ['id', 'product_name', 'product_sold', 'quantity_sold', 'selling_price', 'profit', 'sale_date', 'created_by']
        read_only_fields = ['product_sold', 'created_by']  # Ensure these fields are not editable via the API

    def create(self, validated_data):
        user = self.context['request'].user
        product_name = validated_data.pop('product_name')  # Get the product name string

        # Find the corresponding Inventory object by product name and the user's admin
        try:
            product_instance = Inventory.objects.get(product=product_name, user=user.created_by)
        except Inventory.DoesNotExist:
            raise serializers.ValidationError("Product does not exist or is not associated with this user.")

        # Allow admins and users linked to the admin to bypass the ownership check
        if not user.is_staff and product_instance.user != user.created_by:
            raise serializers.ValidationError("You can only sell from your admin's inventory.")

        validated_data.pop('product_sold', None)
        # Create the sales record (do not pass created_by here, it's already handled by the serializer)
        sale = Sales.objects.create(product_sold=product_instance, **validated_data)

        return sale