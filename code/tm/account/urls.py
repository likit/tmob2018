from django.urls import path
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_change/', auth_views.PasswordChangeView.as_view(),
            name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(),
            name='password_change_done'),
    path('register/', views.register, name='register'),
    path('link_tm_account/<int:new_user_id>/', views.link_tm_account, name='tm_account'),
    path('verify_email/<int:user_id>/<int:profile_id>/', views.verify_email, name='verify_email'),
    path('edit/', views.edit_profile, name='edit_profile'),
    path('social-login/', views.social_login, name='social_login'),
    path('<username>/', views.profile, name='profile'),
    url(r'^register-by-token/(?P<backend>[^/]+)/$', views.register_by_access_token),
    url(r'^activate_link/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<pidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate_link, name='activate_link'),
]
