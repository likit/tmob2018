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
    path('num_abstract_person/', views.show_abstract_per_person,
            name='show_abstract_per_person'),
    path('get_num_active_scholar_studs/', views.get_num_active_scholar_studs,
            name='get_num_active_scholar_studs'),
    path('get_abstract_field/', views.get_abstract_fields,
            name='get_abstract_field'),
    path('get_researcher_by_field/', views.get_researcher_by_field,
         name='get_researcher_by_field'),
    path('get_scholar_joined_tm_ratio/', views.get_scholar_joined_tm_ratio,
         name='get_scholar_joined_tm_ratio'),
    path('get_num_active_scholar_tm/', views.get_num_active_scholar_tm,
         name='get_num_active_scholar_tm'),
    path('get_activeness_scholar_tm/', views.get_activeness_scholar_tm,
         name='get_activeness_scholar_tm'),
    path('get_tm_researchers_graph_data/', views.get_tm_researchers_graph_data,
         name='get_tm_researchers_graph_data'),
    path('scholar-dashboard/', views.show_scholar_dashboard, name='scholar-dashboard'),
    path('tm-dashboard/', views.show_tm_dashboard, name='tm-dashboard'),
    path('network-dashboard/', views.show_network_dashboard, name='network-dashboard')
]