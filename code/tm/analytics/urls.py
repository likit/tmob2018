from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('keywords/', views.res_list, name='res_list'),
    path('nounchunk/', views.noun_chunk_detail, name='noun_chunk')
]