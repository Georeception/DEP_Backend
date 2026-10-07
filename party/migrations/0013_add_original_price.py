from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0012_update_product_model'),
    ]

    # Migration 0009 already adds this field; keep this migration node without repeating the schema change.
    operations = []