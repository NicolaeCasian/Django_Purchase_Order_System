from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom User model with roles
class Role(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class User(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('BUYER', 'Buyer'),
        ('APPROVER', 'Approver'),
        ('INVENTORY_MANAGER', 'Inventory Manager'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='BUYER')

    def __str__(self):
        return self.username

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_info = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

class SportsItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

class PurchaseOrder(models.Model):
    ORDER_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    order_number = models.CharField(max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='PENDING')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"PO {self.order_number}"

class POItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, related_name='items', on_delete=models.CASCADE)
    sports_item = models.ForeignKey(SportsItem, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price per item

    def __str__(self):
        return f"{self.quantity} x {self.sports_item.name} for {self.purchase_order.order_number}"
