from django.contrib import admin
from .models import CustomUser, Inventory, Sales
from .forms import CustomUserChangeForm, CustomUserCreationForm
from django.contrib.auth.admin import UserAdmin

@admin.register(CustomUser)
class CustomAdminUser(admin.ModelAdmin):
        add_form = CustomUserCreationForm
        form = CustomUserChangeForm
        
        model = CustomUser
        
@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity', 'price']
    
@admin.register(Sales)
class SalesAdmin(admin.ModelAdmin):
    list_display = ['product_sold', 'quantity_sold', 'selling_price', 'sale_date', 'profit']
    list_filter = ['sale_date']