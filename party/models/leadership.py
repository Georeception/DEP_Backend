from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from .user import User
from cloudinary_storage.storage import MediaCloudinaryStorage

class LeadershipPosition(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order']

class NationalLeadership(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    position = models.ForeignKey(LeadershipPosition, on_delete=models.CASCADE)
    bio = models.TextField()
    image = models.ImageField(
        upload_to='leadership/',
        storage=MediaCloudinaryStorage(),
        null=True,
        blank=True
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.position.title}"

    class Meta:
        verbose_name_plural = "National Leadership"
        ordering = ['position__order']

@receiver(post_save, sender=NationalLeadership)
def log_image_upload(sender, instance, **kwargs):
    if instance.image:
        print(f"Image uploaded for {instance.name}:")
        print(f"Image path: {instance.image}")
        print(f"Image URL: {instance.image.url}")
        print(f"Image storage: {instance.image.storage}") 