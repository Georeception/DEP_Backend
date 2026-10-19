from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0018_membership_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='membership_type',
            field=models.CharField(
                choices=[
                    ('mwananchi', 'Mwananchi'),
                    ('mca', 'MCA'),
                    ('mp', 'MP'),
                    ('women_rep', 'Women Rep'),
                    ('senator', 'Senator'),
                    ('governor', 'Governor'),
                    ('bronze', 'Bronze'),
                    ('silver', 'Silver'),
                    ('gold', 'Gold'),
                    ('platinum', 'Platinum'),
                ],
                max_length=20,
            ),
        ),
    ]
