# Generated by Django 5.2.1 on 2025-05-14 09:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0006_nationalleadership_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='County',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('code', models.CharField(blank=True, max_length=10, null=True, unique=True)),
            ],
            options={
                'verbose_name_plural': 'Counties',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Constituency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('code', models.CharField(blank=True, max_length=10, null=True, unique=True)),
                ('county', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='constituencies', to='party.county')),
            ],
            options={
                'verbose_name_plural': 'Constituencies',
                'ordering': ['name'],
                'unique_together': {('name', 'county')},
            },
        ),
        migrations.CreateModel(
            name='Ward',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('code', models.CharField(blank=True, max_length=10, null=True, unique=True)),
                ('constituency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wards', to='party.constituency')),
            ],
            options={
                'ordering': ['name'],
                'unique_together': {('name', 'constituency')},
            },
        ),
    ]
