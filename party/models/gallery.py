from django.db import models
from .user import User
import cloudinary
from django.conf import settings
from cloudinary_storage.storage import MediaCloudinaryStorage

class GalleryCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Gallery Categories"

class Gallery(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default='image')
    image = models.ImageField(upload_to='gallery/images/', storage=MediaCloudinaryStorage(), null=True, blank=True)
    video = models.FileField(upload_to='gallery/videos/', storage=MediaCloudinaryStorage(), null=True, blank=True)
    thumbnail = models.ImageField(upload_to='gallery/thumbnails/', storage=MediaCloudinaryStorage(), null=True, blank=True)
    category = models.ForeignKey(GalleryCategory, on_delete=models.CASCADE, related_name='gallery_items')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)

    def get_image_url(self):
        if not self.image:
            return None
        if str(self.image).startswith('v'):
            return f"https://res.cloudinary.com/{settings.CLOUDINARY_STORAGE['CLOUD_NAME']}/image/upload/{self.image}"
        return self.image.url if self.image else None

    def get_thumbnail_url(self):
        if not self.thumbnail:
            return None
        if str(self.thumbnail).startswith('v'):
            return f"https://res.cloudinary.com/{settings.CLOUDINARY_STORAGE['CLOUD_NAME']}/image/upload/{self.thumbnail}"
        return self.thumbnail.url if self.thumbnail else None

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.media_type == 'image' and not self.image:
            raise ValidationError('Image is required for image type media')
        if self.media_type == 'video' and not self.video:
            raise ValidationError('Video is required for video type media')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Gallery"
        ordering = ['-created_at'] 