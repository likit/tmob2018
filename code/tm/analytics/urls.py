from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('keywords/', views.res_list, name='res_list')
]