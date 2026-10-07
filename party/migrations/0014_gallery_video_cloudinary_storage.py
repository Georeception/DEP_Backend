import cloudinary_storage.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0013_add_original_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gallery',
            name='video',
            field=models.FileField(
                blank=True,
                null=True,
                storage=cloudinary_storage.storage.VideoMediaCloudinaryStorage(),
                upload_to='gallery/videos/',
            ),
        ),
    ]
