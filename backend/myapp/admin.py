from django.contrib import admin
from .models import CustomUser, Inventory, Sales
from django.contrib.auth.admin import UserAdmin

@admin.register(CustomUser)
class CustomAdminUser(UserAdmin):
    list_display = ["email", "username", "role", "is_active", "is_staff", "is_superuser"]
    list_filter = ["role", "is_active", "is_staff", "is_superuser"]
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )
    search_fields = ["email", "username"]
    ordering = ["username"]

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity', 'price', 'created_by']  # Replace 'user' with 'created_by'
    list_filter = ['created_by']  # Replace 'user' with 'created_by'
    search_fields = ['product', 'created_by__username']  # Replace 'user__username' with 'created_by__username'
    ordering = ['product']

@admin.register(Sales)
class SalesAdmin(admin.ModelAdmin):
    list_display = ['product_sold', 'quantity_sold', 'selling_price', 'profit', 'sale_date']
    list_filter = ['sale_date', 'product_sold']
    search_fields = ['product_sold__product']
    ordering = ['-sale_date']


# from django.contrib import admin
# from .models import CustomUser, Inventory, Sales
# from django.contrib.auth.admin import UserAdmin

# @admin.register(CustomUser)
# class CustomAdminUser(UserAdmin):
#     list_display = ["email", "username", "role", "is_active", "is_staff", "is_superuser"]
#     list_filter = ["role", "is_active", "is_staff", "is_superuser"]
#     fieldsets = UserAdmin.fieldsets + (
#         ('Custom Fields', {'fields': ('role',)}),
#     )
#     add_fieldsets = UserAdmin.add_fieldsets + (
#         ('Custom Fields', {'fields': ('role',)}),
#     )
#     search_fields = ["email", "username"]
#     ordering = ["username"]

# @admin.register(Inventory)
# class InventoryAdmin(admin.ModelAdmin):
#     list_display = ['product', 'quantity', 'price', 'user']
#     list_filter = ['user']
#     search_fields = ['product', 'user__username']
#     ordering = ['product']

# @admin.register(Sales)
# class SalesAdmin(admin.ModelAdmin):
#     list_display = ['product_sold', 'quantity_sold', 'selling_price', 'profit', 'sale_date']
#     list_filter = ['sale_date', 'product_sold']
#     search_fields = ['product_sold__product']
#     ordering = ['-sale_date']
