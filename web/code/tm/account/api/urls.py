from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('users/',
         views.UserListView.as_view(),
         name='subject_detail'),
    path('users/<pk>/',
         views.UserDetailView.as_view(),
         name='user_detail')
]