# Generated by Django 4.2.7 on 2023-11-19 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
    ]
