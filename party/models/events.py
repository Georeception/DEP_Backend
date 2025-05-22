from django.db import models
from django.utils.text import slugify
from froala_editor.fields import FroalaField
from .user import User
from cloudinary_storage.storage import MediaCloudinaryStorage
import cloudinary.uploader
import os

class EventCategory(models.Model):
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
        verbose_name_plural = "Event Categories"

class Event(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()  # Preview description
    preview_image = models.ImageField(
        upload_to='events/previews/',
        storage=MediaCloudinaryStorage(),
        null=True,
        blank=True
    )
    content = FroalaField()  # Full event details with rich text editor
    category = models.ForeignKey(EventCategory, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Handle preview_image upload
        if self.preview_image and not str(self.preview_image).startswith('v'):
            try:
                file_obj = self.preview_image.file
                file_obj.seek(0)
                result = cloudinary.uploader.upload(
                    file_obj,
                    folder="events/previews",
                    resource_type="image"
                )
                print(f"Cloudinary preview_image upload result: {result}")
                self.preview_image = f"v{result['version']}/{result['public_id']}"
            except Exception as e:
                print(f"Error uploading preview_image to Cloudinary: {str(e)}")

        super().save(*args, **kwargs)

    def get_preview_image_url(self):
        if self.preview_image and str(self.preview_image).startswith('v'):
            return f"https://res.cloudinary.com/dgkommeq9/image/upload/{self.preview_image}"
        return self.preview_image.url if self.preview_image else None

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-start_date']

class EventRegistration(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    additional_info = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.event.title}"

    class Meta:
        unique_together = ('user', 'event') 