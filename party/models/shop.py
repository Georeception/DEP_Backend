from django.db import models
from django.utils.text import slugify
from .user import User

class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Product Categories"

class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_modifier_type = models.CharField(
        max_length=20,
        choices=[
            ('none', 'None'),
            ('multiply', 'Multiply'),
            ('add', 'Add')
        ],
        default='none'
    )
    price_modifier_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Value to multiply or add to the base price'
    )
    image = models.ImageField(upload_to='products/')
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    stock = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_original_price(self):
        if self.price_modifier_type == 'multiply' and self.price_modifier_value > 0:
            return self.price * self.price_modifier_value
        elif self.price_modifier_type == 'add' and self.price_modifier_value > 0:
            return self.price + self.price_modifier_value
        return None

    def calculate_discount(self):
        original = self.calculate_original_price()
        if original and original > self.price:
            return int(((original - self.price) / original) * 100)
        return 0

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        self.original_price = self.calculate_original_price()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="Rating from 1 to 5"
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('product', 'user')  # One review per user per product

    def __str__(self):
        return f"Review by {self.user.get_full_name() or self.user.email} for {self.product.name}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHODS = [
        ('mpesa', 'M-PESA'),
        ('mpesa_stk', 'M-PESA STK Push'),
        ('card', 'Credit/Debit Card'),
        ('bank', 'Bank Transfer'),
        ('paypal', 'PayPal'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    
    # Payment provider specific fields
    payment_provider = models.CharField(max_length=50)  # e.g., 'mpesa', 'stripe', 'paypal'
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    payment_provider_response = models.JSONField(null=True, blank=True)
    
    # Order details
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order_number}"

    class Meta:
        ordering = ['-created_at']

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of purchase

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    class Meta:
        unique_together = ('order', 'product') 