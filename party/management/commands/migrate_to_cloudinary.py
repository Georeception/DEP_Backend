from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.conf import settings
import cloudinary
import cloudinary.uploader
from party.models import NationalLeadership
import os

class Command(BaseCommand):
    help = 'Migrate existing media files to Cloudinary'

    def handle(self, *args, **options):
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
            api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
            api_secret=settings.CLOUDINARY_STORAGE['API_SECRET']
        )

        # Get all leadership entries
        leaders = NationalLeadership.objects.all()
        
        for leader in leaders:
            if leader.image and not str(leader.image).startswith('v'):
                try:
                    # Get the local file path
                    local_path = leader.image.path
                    
                    if os.path.exists(local_path):
                        # Upload to Cloudinary
                        result = cloudinary.uploader.upload(
                            local_path,
                            folder="leadership",
                            resource_type="image"
                        )
                        
                        # Update the image field with Cloudinary version
                        leader.image = result['version'] + '/' + result['public_id']
                        leader.save()
                        
                        self.stdout.write(
                            self.style.SUCCESS(f'Successfully migrated image for {leader.name}')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'Image file not found for {leader.name}: {local_path}')
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error migrating image for {leader.name}: {str(e)}')
                    ) 