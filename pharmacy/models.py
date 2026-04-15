# pharmacy/models.py  — COMPLETE FILE
# Added: PharmacyOrder model for eSewa payment tracking

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = [('admin','Admin'),('pharmacist','Pharmacist')]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='pharmacist')
    class Meta:
        app_label = 'pharmacy'
    def __str__(self):
        return f"{self.username} ({self.role})"


class Category(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    class Meta:
        app_label           = 'pharmacy'
        verbose_name_plural = 'Categories'
    def __str__(self):
        return self.name


class Medicine(models.Model):
    name                = models.CharField(max_length=200)
    category            = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                             null=True, blank=True)
    price               = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity      = models.PositiveIntegerField(default=0)
    expiry_date         = models.DateField()
    manufacturer        = models.DateField()
    description = models.TextField(blank=True, null=True)
    low_stock_threshold = models.PositiveIntegerField(default=10)
    image               = models.ImageField(upload_to='medicines/', blank=True, null=True)
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)
    class Meta:
        app_label = 'pharmacy'
    def is_low_stock(self):
        return self.stock_quantity <= self.low_stock_threshold
    def is_expired(self):
        from django.utils import timezone
        return self.expiry_date < timezone.now().date()
    def __str__(self):
        return self.name


class Bill(models.Model):
    STATUS = [('pending','Pending'),('completed','Completed'),('cancelled','Cancelled')]
    bill_number    = models.CharField(max_length=20, unique=True)
    pharmacist     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    customer_name  = models.CharField(max_length=200, blank=True, default='Walk-in Customer')
    customer_phone = models.CharField(max_length=15, blank=True)
    total_amount   = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status         = models.CharField(max_length=20, choices=STATUS, default='completed')
    created_at     = models.DateTimeField(auto_now_add=True)
    notes          = models.TextField(blank=True)
    class Meta:
        app_label = 'pharmacy'
    def __str__(self):
        return f"Bill #{self.bill_number}"


class BillItem(models.Model):
    bill       = models.ForeignKey(Bill, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity   = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        app_label = 'pharmacy'
    @property
    def subtotal(self):
        return self.quantity * self.unit_price
    def __str__(self):
        return f"{self.medicine.name} × {self.quantity}"


class CartItem(models.Model):
    user     = models.ForeignKey(User, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        app_label       = 'pharmacy'
        unique_together = ('user', 'medicine')
    @property
    def subtotal(self):
        return self.medicine.price * self.quantity
    def __str__(self):
        return f"{self.user.username} — {self.medicine.name} × {self.quantity}"

class PharmacyOrder(models.Model):
    """
    Created when user clicks 'Order Now' or 'Order All' from cart.
    Stores delivery info + payment method + eSewa payment status.
    """
    PAYMENT_CHOICES = [
        ('esewa', 'eSewa'),
        ('cash',  'Cash on Delivery'),
    ]
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('paid',      'Paid'),
        ('failed',    'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    user             = models.ForeignKey(User, on_delete=models.CASCADE)
    medicine         = models.ForeignKey(Medicine, on_delete=models.PROTECT)
    cart_item        = models.ForeignKey(CartItem, on_delete=models.SET_NULL,
     null=True, blank=True)
    quantity         = models.PositiveIntegerField()
    total_price      = models.DecimalField(max_digits=12, decimal_places=2)
    address          = models.TextField()
    contact_no       = models.CharField(max_length=15)
    payment_method   = models.CharField(max_length=10,
    choices=PAYMENT_CHOICES, default='cash')
    payment_status   = models.CharField(max_length=15,
    choices=STATUS_CHOICES, default='pending')
    # eSewa stores a unique transaction UUID for each payment
    transaction_uuid = models.CharField(max_length=100, blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'pharmacy'

    def __str__(self):
        return f"Order #{self.pk} — {self.medicine.name} [{self.payment_status}]"