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

    # Section E: Special Category
    special_category = models.CharField(max_length=50, null=True, blank=True, help_text="Woman, Youth, PWD, or None")
    disability_nature = models.CharField(max_length=255, null=True, blank=True, help_text="Nature of disability if PWD")

    # Section F: Education, Profession & Experience
    education_level = models.CharField(max_length=50, null=True, blank=True, help_text="Primary, Secondary, Certificate, Diploma, Degree, Postgraduate, Other")
    professional_qualifications = models.TextField(null=True, blank=True)
    current_occupation = models.CharField(max_length=255, null=True, blank=True)
    current_employer = models.CharField(max_length=255, null=True, blank=True)
    professional_experience = models.TextField(null=True, blank=True, help_text="Brief description of professional, leadership, community experience")

    # Section G: Leadership & Community Engagement
    previous_leadership_position = models.CharField(max_length=10, choices=[('yes', 'Yes'), ('no', 'No')], null=True, blank=True)
    previous_leadership_details = models.TextField(null=True, blank=True, help_text="Position, institution, period")
    organizations_participated = models.TextField(null=True, blank=True, help_text="Leadership, community, professional, youth, women, religious or civic organisations")
    community_contribution = models.TextField(null=True, blank=True, help_text="Brief statement of contribution to community development")

    # Section H: Motivation for DEP-BUS Ticket
    motivation_reason = models.TextField(null=True, blank=True, help_text="Why you wish to contest on DEP-BUS ticket")
    key_issues = models.TextField(null=True, blank=True, help_text="Three most important issues to address")
    devolution_understanding = models.TextField(null=True, blank=True, help_text="What devolution means to you and how to strengthen it")
    contribution_to_party = models.TextField(null=True, blank=True, help_text="What you would bring to DEP-BUS and the people")

    # Section I: Political & Electoral Information
    contested_before = models.CharField(max_length=10, choices=[('yes', 'Yes'), ('no', 'No')], null=True, blank=True)
    contested_details = models.TextField(null=True, blank=True, help_text="Position, year, party, outcome")
    current_public_office = models.CharField(max_length=10, choices=[('yes', 'Yes'), ('no', 'No')], null=True, blank=True)
    current_office_details = models.CharField(max_length=255, null=True, blank=True)
    bankruptcy_proceedings = models.CharField(max_length=10, choices=[('yes', 'Yes'), ('no', 'No')], null=True, blank=True)
    bankruptcy_details = models.TextField(null=True, blank=True)
    criminal_proceedings = models.CharField(max_length=10, choices=[('yes', 'Yes'), ('no', 'No')], null=True, blank=True)
    criminal_proceedings_details = models.TextField(null=True, blank=True)

    # Section J: Campaign & Organisational Capacity
    support_network = models.TextField(null=True, blank=True, help_text="Description of support/network within electoral area")
    volunteer_count = models.IntegerField(null=True, blank=True, help_text="Estimated number of volunteers/supporters")
    campaign_structure = models.CharField(max_length=50, choices=[('yes', 'Yes'), ('no', 'No'), ('in_development', 'In Development')], null=True, blank=True)
    grassroots_strategy = models.TextField(null=True, blank=True, help_text="Proposed grassroots organisation strategy")

    # Section K: Commitment to DEP-BUS
    uphold_values = models.CharField(max_length=10, choices=[('yes', 'Yes'), ('no', 'No')], null=True, blank=True)
    peaceful_politics = models.CharField(max_length=10, choices=[('yes', 'Yes'), ('no', 'No')], null=True, blank=True)
    issue_based_politics = models.CharField(max_length=10, choices=[('yes', 'Yes'), ('no', 'No')], null=True, blank=True)
    abide_nomination = models.CharField(max_length=10, choices=[('yes', 'Yes'), ('no', 'No')], null=True, blank=True)

    # Section M: Document Attachments (Cloudinary URLs)
    id_document = models.CharField(max_length=500, null=True, blank=True, help_text="Cloudinary URL for National ID/Passport")
    passport_photo = models.CharField(max_length=500, null=True, blank=True, help_text="Cloudinary URL for Passport-size photograph")
    membership_proof = models.CharField(max_length=500, null=True, blank=True, help_text="Cloudinary URL for DEP-BUS membership proof")
    academic_certificates = models.TextField(null=True, blank=True, help_text="Cloudinary URLs for academic/professional certificates (comma-separated)")
    leadership_documents = models.TextField(null=True, blank=True, help_text="Cloudinary URLs for leadership/public service documentation (comma-separated)")
    other_documents = models.TextField(null=True, blank=True, help_text="Cloudinary URLs for other supporting documents (comma-separated)")

    # Application Status (for admin use)
    application_status = models.CharField(
        max_length=50,
        choices=[
            ('received', 'Received'),
            ('under_review', 'Under Review'),
            ('approved', 'Approved for Further Consideration'),
            ('requires_info', 'Requires Additional Information'),
            ('not_approved', 'Not Approved'),
        ],
        default='received',
    )
    membership_status_verified = models.BooleanField(default=False)
    documents_verified = models.BooleanField(default=False)
    admin_remarks = models.TextField(null=True, blank=True)

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