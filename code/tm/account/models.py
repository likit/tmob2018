# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from datetime import datetime

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    title = models.CharField(max_length=40, blank=True)
    first_name_th = models.CharField(max_length=255, blank=False)
    last_name_th = models.CharField(max_length=255, blank=False)
    scholarship = models.BooleanField(default=False)
    college = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)
    scopus_id = models.CharField(max_length=255, blank=True)
    degree = models.IntegerField(choices=(
                                    (1, u'ปริญญาตรี'),
                                    (2, u'ปริญญาโท'),
                                    (3, u'ปริญญาเอก')
                                    ), blank=True, null=True)
    graduated_at = models.DateField(blank=True, null=True)
    field_of_study = models.CharField(max_length=255, blank=True)
    specialty = models.CharField(max_length=255, blank=True)
    designated_affiliation = models.CharField(max_length=255, blank=True)  # affiliation of the student after graduate
    photo = models.ImageField(upload_to='users/%Y/%m/%d', blank=True)
    social_photo = models.CharField(max_length=255, blank=True)
    current_position = models.CharField(max_length=255, blank=True)
    current_affiliation = models.CharField(max_length=255, blank=True)
    about = models.TextField(blank=True)


    def __str__(self):
        return 'Profile for user {}'.format(self.user.username)

