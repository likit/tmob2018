from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('switchlang/', views.switch_lang, name='switchlang')
]
