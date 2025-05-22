from django.db import models
from django.utils.text import slugify
from froala_editor.fields import FroalaField
from .user import User
from cloudinary_storage.storage import MediaCloudinaryStorage
import cloudinary.uploader
import os

class NewsCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "News Categories"
        ordering = ['name']

class News(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()  # Preview description
    preview_image = models.ImageField(
        upload_to='news/previews/',
        storage=MediaCloudinaryStorage(),
        null=True,
        blank=True
    )
    content = FroalaField()  # Full article content with rich text editor
    category = models.ForeignKey(NewsCategory, on_delete=models.CASCADE, related_name='news')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='news')
    image = models.ImageField(
        upload_to='news/',
        storage=MediaCloudinaryStorage(),
        null=True,
        blank=True
    )
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
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
                    folder="news/previews",
                    resource_type="image"
                )
                print(f"Cloudinary preview_image upload result: {result}")
                self.preview_image = f"v{result['version']}/{result['public_id']}"
            except Exception as e:
                print(f"Error uploading preview_image to Cloudinary: {str(e)}")

        # Handle main image upload
        if self.image and not str(self.image).startswith('v'):
            try:
                file_obj = self.image.file
                file_obj.seek(0)
                result = cloudinary.uploader.upload(
                    file_obj,
                    folder="news",
                    resource_type="image"
                )
                print(f"Cloudinary image upload result: {result}")
                self.image = f"v{result['version']}/{result['public_id']}"
            except Exception as e:
                print(f"Error uploading image to Cloudinary: {str(e)}")

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "News"
        ordering = ['-published_at', '-created_at'] 