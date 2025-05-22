from django.db import models
from .user import User
from cloudinary_storage.storage import MediaCloudinaryStorage
import cloudinary.uploader
import os

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
    image = models.ImageField(
        upload_to='gallery/images/',
        storage=MediaCloudinaryStorage(),
        null=True,
        blank=True
    )
    video = models.FileField(
        upload_to='gallery/videos/',
        storage=MediaCloudinaryStorage(),
        null=True,
        blank=True
    )
    thumbnail = models.ImageField(
        upload_to='gallery/thumbnails/',
        storage=MediaCloudinaryStorage(),
        null=True,
        blank=True
    )
    category = models.ForeignKey(GalleryCategory, on_delete=models.CASCADE, related_name='gallery_items')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Handle image upload
        if self.media_type == 'image' and self.image and not str(self.image).startswith('v'):
            try:
                file_obj = self.image.file
                file_obj.seek(0)
                result = cloudinary.uploader.upload(
                    file_obj,
                    folder="gallery/images",
                    resource_type="image"
                )
                print(f"Cloudinary image upload result: {result}")
                self.image = f"v{result['version']}/{result['public_id']}"
            except Exception as e:
                print(f"Error uploading image to Cloudinary: {str(e)}")

        # Handle video upload
        if self.media_type == 'video' and self.video and not str(self.video).startswith('v'):
            try:
                file_obj = self.video.file
                file_obj.seek(0)
                result = cloudinary.uploader.upload(
                    file_obj,
                    folder="gallery/videos",
                    resource_type="video"
                )
                print(f"Cloudinary video upload result: {result}")
                self.video = f"v{result['version']}/{result['public_id']}"
            except Exception as e:
                print(f"Error uploading video to Cloudinary: {str(e)}")

        # Handle thumbnail upload
        if self.thumbnail and not str(self.thumbnail).startswith('v'):
            try:
                file_obj = self.thumbnail.file
                file_obj.seek(0)
                result = cloudinary.uploader.upload(
                    file_obj,
                    folder="gallery/thumbnails",
                    resource_type="image"
                )
                print(f"Cloudinary thumbnail upload result: {result}")
                self.thumbnail = f"v{result['version']}/{result['public_id']}"
            except Exception as e:
                print(f"Error uploading thumbnail to Cloudinary: {str(e)}")

        super().save(*args, **kwargs)

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