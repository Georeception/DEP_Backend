import froala_editor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0016_paystack_membership_transactions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nationalleadership',
            name='bio',
            field=froala_editor.fields.FroalaField(),
        ),
    ]
