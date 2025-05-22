from django.db import models
from django.utils.text import slugify
from froala_editor.fields import FroalaField
from .user import User
import cloudinary
from django.conf import settings

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
    preview_image = models.ImageField(upload_to='news/previews/')
    content = FroalaField()  # Full article content with rich text editor
    category = models.ForeignKey(NewsCategory, on_delete=models.CASCADE, related_name='news')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='news')
    image = models.ImageField(upload_to='news/', null=True, blank=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_preview_image_url(self):
        if not self.preview_image:
            return None
        if str(self.preview_image).startswith('v'):
            return f"https://res.cloudinary.com/{settings.CLOUDINARY_STORAGE['CLOUD_NAME']}/image/upload/{self.preview_image}"
        try:
            public_id = str(self.preview_image)
            if public_id.startswith('news/previews/'):
                cloudinary_path = public_id
            else:
                filename = public_id.split('/')[-1]
                cloudinary_path = f"news/previews/{filename}"
            result = cloudinary.uploader.explicit(cloudinary_path, type="upload")
            return result['secure_url']
        except Exception as e:
            print(f"Error getting Cloudinary URL for preview image: {str(e)}")
            return f"{settings.MEDIA_URL}{self.preview_image}"

    def get_image_url(self):
        if not self.image:
            return None
        if str(self.image).startswith('v'):
            return f"https://res.cloudinary.com/{settings.CLOUDINARY_STORAGE['CLOUD_NAME']}/image/upload/{self.image}"
        try:
            public_id = str(self.image)
            if public_id.startswith('news/'):
                cloudinary_path = public_id
            else:
                filename = public_id.split('/')[-1]
                cloudinary_path = f"news/{filename}"
            result = cloudinary.uploader.explicit(cloudinary_path, type="upload")
            return result['secure_url']
        except Exception as e:
            print(f"Error getting Cloudinary URL for image: {str(e)}")
            return f"{settings.MEDIA_URL}{self.image}"

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "News"
        ordering = ['-published_at', '-created_at'] 