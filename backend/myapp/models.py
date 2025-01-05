from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ADMIN = 'admin'
    USER = 'user'

    ROLE_CHOICES = [
        (ADMIN, 'admin'),
        (USER, 'user'),
    ]
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=USER)
    created_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='created_users')


    USERNAME_FIELD="email"
    REQUIRED_FIELDS=["username"]
    
    def __str__(self) -> str:
        return self.email
    

class Inventory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="inventories")
    product = models.CharField(max_length=20)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.product
    
class Sales(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sales_user")  # You can leave this as is
    product_sold = models.ForeignKey(Inventory, on_delete=models.CASCADE) 
    quantity_sold = models.IntegerField(default=0)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateTimeField(auto_now_add=True)
    profit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sales_created_by")

    

    def save(self, *args, **kwargs):
        # Ensure the inventory belongs to the admin who created the sales user
        # if self.product_sold.user != self.user.created_by:
        #     raise ValueError("Sales user and Inventory user mismatch with the admin user")
        if self.user.role != 'admin' and self.product_sold.user != self.user.created_by:
            raise ValueError("Sales user can only sell inventory assigned by their admin user")

        # Admins can sell inventory that they own
        if self.user.role == 'admin' and self.product_sold.user != self.user:
            raise ValueError("Admin can only sell their own inventory")


        # Check if there is enough quantity in stock
        if self.product_sold.quantity < self.quantity_sold:
            raise ValueError("Not enough stock to complete the sale")

        # Deduct quantity from inventory
        self.product_sold.quantity -= self.quantity_sold
        self.product_sold.save()  # Save the updated quantity in the inventory

        # Calculate cost from inventory
        total_cost = self.product_sold.price * self.quantity_sold
        # Calculate total selling price
        total_selling_price = self.selling_price * self.quantity_sold
        # Calculate profit
        self.profit = total_selling_price - total_cost

        super(Sales, self).save(*args, **kwargs)

    def __str__(self):
        return f"Sale of {self.product_sold.product} by {self.user} on {self.sale_date}" 