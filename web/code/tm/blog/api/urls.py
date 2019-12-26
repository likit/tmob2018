from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('posts/',
        views.PostPageListView.as_view(),
        name='post_list'),
    path('posts/<pk>/',
        views.PostPageDetailView.as_view(),
        name='post_detail'),
]