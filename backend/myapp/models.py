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
    created_by = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, related_name='created_users'
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self) -> str:
        return self.email


class Inventory(models.Model):
    product = models.CharField(max_length=20)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="inventories"
    )

    def __str__(self):
        return self.product


class Sales(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="sales"
    )  # User making the sale
    product_sold = models.ForeignKey(
        Inventory, on_delete=models.CASCADE, related_name="sales"
    )
    quantity_sold = models.IntegerField(default=0)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateTimeField(auto_now_add=True)
    profit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="sales_created_by"
    )  # Admin who created the sale

    def save(self, *args, **kwargs):
        # Restrict sales based on user-admin relationship
        if self.user.role != 'admin' and self.product_sold.created_by != self.user.created_by:
            raise ValueError("Users can only sell inventory assigned by their admin.")

        # Admins can sell inventory they own
        if self.user.role == 'admin' and self.product_sold.created_by != self.user:
            raise ValueError("Admins can only sell their own inventory.")

        super(Sales, self).save(*args, **kwargs)

    def __str__(self):
        return f"Sale of {self.product_sold.product} by {self.user} on {self.sale_date}"


