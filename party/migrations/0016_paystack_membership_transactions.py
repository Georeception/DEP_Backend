from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0015_county_country'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='transaction_id',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='membership',
            name='payment_method',
            field=models.CharField(
                blank=True,
                choices=[
                    ('mpesa', 'M-PESA'),
                    ('airtel', 'Airtel Money'),
                    ('card', 'Credit/Debit Card'),
                    ('bank', 'Bank Transfer'),
                    ('paypal', 'PayPal'),
                    ('stripe', 'Stripe'),
                    ('paystack', 'Paystack'),
                ],
                max_length=20,
                null=True,
            ),
        ),
    ]
