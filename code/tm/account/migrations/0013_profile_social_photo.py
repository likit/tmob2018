# Generated by Django 2.0.6 on 2018-06-25 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0012_profile_scopus_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='social_photo',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]