from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('database/', views.main_db, name='database'),
    path('keywords/', views.res_list, name='res_list'),
    path('nounchunk/', views.noun_chunk_detail, name='noun_chunk'),
    path('profile/<int:author_id>/', views.show_profile, name='show_profile'),
    path('profile-by-name/', views.show_profile_by_name, name='show_profile_by_name'),
    path('show_field/<field_name>/', views.show_field, name='show_field'),
    path('abstract/<abstract_id>/', views.show_abstract, name='show_abstract'),
]