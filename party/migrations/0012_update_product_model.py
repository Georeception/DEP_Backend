from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0011_pickuplocation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='price_modifier_type',
            field=models.CharField(choices=[('multiply', 'Multiply'), ('add', 'Add')], default='multiply', max_length=10),
        ),
        migrations.AlterField(
            model_name='product',
            name='price_modifier_value',
            field=models.DecimalField(decimal_places=2, default=1.0, max_digits=10),
        ),
    ] 