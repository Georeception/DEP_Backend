from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from .user import User
from cloudinary_storage.storage import MediaCloudinaryStorage
import cloudinary.uploader
import os

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

    def save(self, *args, **kwargs):
        if self.image and not str(self.image).startswith('v'):
            try:
                # Get the local file path
                local_path = self.image.path
                if os.path.exists(local_path):
                    # Upload to Cloudinary
                    result = cloudinary.uploader.upload(
                        local_path,
                        folder="leadership",
                        resource_type="image"
                    )
                    print(f"Cloudinary upload result: {result}")
                    # Update the image field with Cloudinary version
                    self.image = result['version'] + '/' + result['public_id']
            except Exception as e:
                print(f"Error uploading to Cloudinary: {str(e)}")
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "National Leadership"
        ordering = ['position__order']

@receiver(post_save, sender=NationalLeadership)
def log_image_upload(sender, instance, **kwargs):
    if instance.image:
        print(f"\nImage details for {instance.name}:")
        print(f"Image path: {instance.image}")
        print(f"Image URL: {instance.image.url}")
        print(f"Image storage: {instance.image.storage}")
        print(f"Is Cloudinary URL: {str(instance.image).startswith('v')}") 