# Generated by Django 2.0.6 on 2018-06-23 03:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_profile_scholarship'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='graduate_at',
            new_name='graduated_at',
        ),
    ]