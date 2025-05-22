from django.db import models
from django.utils.text import slugify
from froala_editor.fields import FroalaField
from .user import User

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
        if self.preview_image and str(self.preview_image).startswith('v'):
            return f"https://res.cloudinary.com/dgkommeq9/image/upload/{self.preview_image}"
        return self.preview_image.url if self.preview_image else None

    def get_image_url(self):
        if self.image and str(self.image).startswith('v'):
            return f"https://res.cloudinary.com/dgkommeq9/image/upload/{self.image}"
        return self.image.url if self.image else None

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "News"
        ordering = ['-published_at', '-created_at'] 