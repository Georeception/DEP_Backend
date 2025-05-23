from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0012_update_product_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='original_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ] 