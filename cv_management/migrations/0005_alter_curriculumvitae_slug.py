# Generated by Django 4.2.7 on 2023-11-25 21:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cv_management', '0004_alter_curriculumvitae_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='curriculumvitae',
            name='slug',
            field=models.SlugField(blank=True, default='', null=True),
        ),
    ]