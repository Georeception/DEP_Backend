from django.db import models
from .user import User

class Donation(models.Model):
    PAYMENT_METHODS = [
        ('mpesa', 'M-PESA'),
        ('mpesa_stk', 'M-PESA STK Push'),
        ('card', 'Credit/Debit Card'),
        ('bank', 'Bank Transfer'),
        ('paypal', 'PayPal'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Payment provider specific fields
    payment_provider = models.CharField(max_length=50)  # e.g., 'mpesa', 'stripe', 'paypal'
    payment_provider_response = models.JSONField(null=True, blank=True)
    
    # Donor information
    donor_name = models.CharField(max_length=200)
    donor_email = models.EmailField()
    donor_phone = models.CharField(max_length=20)
    message = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.donor_name} - {self.amount} - {self.status}"
    
    class Meta:
        ordering = ['-created_at'] 