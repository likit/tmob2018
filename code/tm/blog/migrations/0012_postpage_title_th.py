# Generated by Django 2.0.6 on 2018-07-03 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0011_auto_20180703_1401'),
    ]

    operations = [
        migrations.AddField(
            model_name='postpage',
            name='title_th',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]
