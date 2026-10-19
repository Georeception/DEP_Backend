from datetime import date
from decimal import Decimal

from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
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
        ('mca', 'MCA'),
        ('mp', 'MP'),
        ('women_rep', 'Women Rep'),
        ('senator', 'Senator'),
        ('governor', 'Governor'),
        # Keep existing values valid for historical membership records.
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum')
    ]

    MEMBERSHIP_CATEGORIES = [
        ('general', 'General'),
        ('youth_pwd', 'Youth & people with disability'),
    ]

    DEP_BUS_MEMBERSHIP_STATUSES = [
        ('yes', 'Yes'),
        ('no', 'No'),
        ('not_sure', 'Not Sure'),
    ]

    FREE_REGISTRATION_END = date(2026, 11, 30)

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
        ('stripe', 'Stripe'),
        ('paystack', 'Paystack'),
    ]

    MEMBERSHIP_AMOUNTS = {
        'mwananchi': Decimal('0.00'),
        'mca': Decimal('5000.00'),
        'mp': Decimal('10000.00'),
        'women_rep': Decimal('10000.00'),
        'senator': Decimal('10000.00'),
        'governor': Decimal('50000.00'),
        # Retain the original rates for existing integrations and records.
        'bronze': Decimal('5000.00'),
        'silver': Decimal('10000.00'),
        'gold': Decimal('25000.00'),
        'platinum': Decimal('50000.00')
    }

    YOUTH_PWD_MEMBERSHIP_AMOUNTS = {
        'mca': Decimal('2500.00'),
        'mp': Decimal('5000.00'),
        'women_rep': Decimal('5000.00'),
        'senator': Decimal('5000.00'),
        'governor': Decimal('25000.00'),
    }

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    membership_type = models.CharField(max_length=20, choices=MEMBERSHIP_TYPES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, null=True, blank=True)
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    membership_category = models.CharField(
        max_length=20,
        choices=MEMBERSHIP_CATEGORIES,
        default='general',
    )
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
    full_name = models.CharField(max_length=200, blank=True, default='')
    national_id_number = models.CharField(max_length=50, blank=True, default='')
    date_of_birth = models.DateField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True, default='')
    sub_county = models.CharField(max_length=100, blank=True, default='')
    postal_address = models.CharField(max_length=255, blank=True, default='')
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True)
    constituency = models.ForeignKey(Constituency, on_delete=models.SET_NULL, null=True)
    ward = models.ForeignKey(Ward, on_delete=models.SET_NULL, null=True)
    electoral_county = models.ForeignKey(
        County,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='aspirant_memberships',
    )
    electoral_constituency = models.ForeignKey(
        Constituency,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='aspirant_memberships',
    )
    electoral_ward = models.ForeignKey(
        Ward,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='aspirant_memberships',
    )
    dep_bus_membership_status = models.CharField(
        max_length=10,
        choices=DEP_BUS_MEMBERSHIP_STATUSES,
        blank=True,
        default='',
    )
    membership_status_confirmed = models.BooleanField(null=True, blank=True)
    membership_reference = models.CharField(max_length=100, blank=True, default='')
    aspirant_details = models.JSONField(default=dict, blank=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    occupation = models.CharField(max_length=100, null=True, blank=True)
    interests = models.TextField(null=True, blank=True)

    @classmethod
    def get_amount(cls, membership_type, membership_category='general'):
        if membership_category == 'youth_pwd':
            return cls.YOUTH_PWD_MEMBERSHIP_AMOUNTS.get(membership_type)
        return cls.MEMBERSHIP_AMOUNTS.get(membership_type)

    @classmethod
    def is_free_registration_period(cls):
        return timezone.localdate() <= cls.FREE_REGISTRATION_END

    def save(self, *args, **kwargs):
        if self.amount == Decimal('0.00') and not (
            self.payment_status == 'completed' and self.payment_method is None
        ):
            self.amount = self.get_amount(self.membership_type, self.membership_category) or Decimal('0.00')
        super().save(*args, **kwargs)

    def __str__(self):
        if self.user:
            return f"{self.user.email} - {self.membership_type}"
        return f"{self.email} - {self.membership_type}"

    class Meta:
        ordering = ['-created_at'] 