from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0017_leadership_bio_froala'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='membership_category',
            field=models.CharField(
                choices=[
                    ('general', 'General'),
                    ('youth_pwd', 'Youth & people with disability'),
                ],
                default='general',
                max_length=20,
            ),
        ),
    ]
