from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD="email"
    REQUIRED_FIELDS=["username"]
    
    def __str__(self) -> str:
        return self.email
    

# class User(AbstractUser):
#     # Add related_name attributes to avoid conflicts
#     groups = models.ManyToManyField(
#         'auth.Group',
#         related_name='custom_user_set',  # Change this to avoid conflict
#         blank=True,
#         help_text='The groups this user belongs to.',
#         verbose_name='groups',
#     )
#     user_permissions = models.ManyToManyField(
#         'auth.Permission',
#         related_name='custom_user_permissions_set',  # Change this to avoid conflict
#         blank=True,
#         help_text='Specific permissions for this user.',
#         verbose_name='user permissions',
#     )


class Inventory(models.Model):
    product = models.CharField(max_length=20)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.product
    
class Sales(models.Model):
    product = models.ForeignKey(Inventory, on_delete=models.CASCADE)  # link to inventory item
    quantity_sold = models.IntegerField(default=0)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateTimeField(auto_now_add=True)
    profit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Check if there is enough quantity in stock
        if self.product.quantity < self.quantity_sold:
            raise ValueError("Not enough stock to complete the sale")

        # Deduct quantity from inventory
        self.product.quantity -= self.quantity_sold
        self.product.save()  # Save the updated quantity in the inventory

        # Calculate cost from inventory
        total_cost = self.product.price * self.quantity_sold
        # Calculate total selling price
        total_selling_price = self.selling_price * self.quantity_sold
        # Calculate profit
        self.profit = total_selling_price - total_cost

        super(Sales, self).save(*args, **kwargs)
