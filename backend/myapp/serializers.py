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
        fields = ['id', 'username', 'email', 'password', 'password2', 'role']
        read_only_fields = ['id']

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
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Inventory
        fields = ['id', 'product', 'quantity', 'price', 'created_by']
        read_only_fields = ['created_by']

    def validate(self, attrs):
        # Ensure admins can only add inventory to their own account
        user = self.context['request'].user
        if user.role != 'admin':
            raise serializers.ValidationError("Only admins can add inventory.")
        return attrs

class SalesSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())  # User making the sale (read-only)
    product_name = serializers.CharField(write_only=True)  # Expecting product name as input
    product_sold = serializers.CharField(source='product_sold.product', read_only=True)  # Display product name (read-only)

    class Meta:
        model = Sales
        fields = ['id', 'product_name', 'product_sold', 'quantity_sold', 'selling_price', 'profit', 'sale_date', 'created_by']
        read_only_fields = ['product_sold', 'created_by']  # These fields should not be editable via the API

    def create(self, validated_data):
        user = self.context['request'].user  # Get the logged-in user
        product_name = validated_data.pop('product_name')  # Get the product name string

        # Admins: Look for products they own directly
        if user.role == 'admin':
            try:
                product_instance = Inventory.objects.get(product=product_name, created_by=user)
            except Inventory.DoesNotExist:
                raise serializers.ValidationError("Product does not exist or is not associated with this admin.")
        # Users: Look for products owned by their associated admin
        else:
            try:
                product_instance = Inventory.objects.get(product=product_name, created_by=user.created_by)
            except Inventory.DoesNotExist:
                raise serializers.ValidationError("Product does not exist or is not associated with your admin.")

        if product_instance.quantity < validated_data['quantity_sold']:
            raise serializers.ValidationError("Not enough stock to complete the sale.")

        # Update the inventory
        product_instance.quantity -= validated_data['quantity_sold']
        product_instance.save()

        # Calculate profit
        validated_data['profit'] = (
            validated_data['selling_price'] * validated_data['quantity_sold']
        ) - (product_instance.price * validated_data['quantity_sold'])

        # Set the user who is making the sale
        validated_data['user'] = user 

        validated_data.pop('product_sold', None)

        sale = Sales.objects.create(product_sold=product_instance, **validated_data)

        return sale

    def to_representation(self, instance):
        """
        Customize the representation based on the user's role:
        - Admins see all related sales, but filter by their own inventory
        - Admins also see sales of the users they have created/registered
        - Users only see their sales
        """
        request = self.context.get('request')
        if request is not None and request.user is not None:
            if request.user.role == 'user' and instance.created_by != request.user:
                raise serializers.ValidationError("You can only view your own sales.")

            # Admins can view sales made by users they have created/registered
            if request.user.role == 'admin':
                # If the sale's created_by is either the admin or a user created by the admin, show it
                if instance.product_sold.created_by != request.user and instance.created_by != request.user:
                    raise serializers.ValidationError("You can only view sales of your products or users you registered.")
        else:
            raise serializers.ValidationError("Request user is not available in the context.")

        return super().to_representation(instance)