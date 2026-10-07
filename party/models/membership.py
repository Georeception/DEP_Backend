from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from .user import User
from .locations import County, Constituency, Ward

class MembershipPlan(models.Model):
    title = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['amount']

class Membership(models.Model):
    MEMBERSHIP_TYPES = [
        ('mwananchi', 'Mwananchi'),
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum')
    ]

    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ]

    PAYMENT_METHODS = [
        ('mpesa', 'M-PESA'),
        ('airtel', 'Airtel Money'),
        ('card', 'Credit/Debit Card'),
        ('bank', 'Bank Transfer'),
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe')
    ]

    MEMBERSHIP_AMOUNTS = {
        'mwananchi': Decimal('0.00'),
        'bronze': Decimal('5000.00'),
        'silver': Decimal('10000.00'),
        'gold': Decimal('25000.00'),
        'platinum': Decimal('50000.00')
    }

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    membership_type = models.CharField(max_length=20, choices=MEMBERSHIP_TYPES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, null=True, blank=True)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # For non-logged in Mwananchi applications
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True)
    constituency = models.ForeignKey(Constituency, on_delete=models.SET_NULL, null=True)
    ward = models.ForeignKey(Ward, on_delete=models.SET_NULL, null=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    occupation = models.CharField(max_length=100, null=True, blank=True)
    interests = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Set amount based on membership type if not already set
        if not self.amount or self.amount == Decimal('0.00'):
            self.amount = self.MEMBERSHIP_AMOUNTS.get(self.membership_type, Decimal('0.00'))
        super().save(*args, **kwargs)

    def __str__(self):
        if self.user:
            return f"{self.user.email} - {self.membership_type}"
        return f"{self.email} - {self.membership_type}"

    class Meta:
        ordering = ['-created_at'] 