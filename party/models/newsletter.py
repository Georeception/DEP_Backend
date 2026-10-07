from django.db import models
import secrets

class NewsletterSubscription(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
    )

    email = models.EmailField(unique=True)
    subscription_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email

    def generate_verification_token(self):
        """
        Generate a secure random token for email verification
        """
        token = secrets.token_urlsafe(32)
        self.verification_token = token
        self.save()
        return token

    class Meta:
        verbose_name = 'Newsletter Subscription'
        verbose_name_plural = 'Newsletter Subscriptions'
        ordering = ['-subscription_date'] 