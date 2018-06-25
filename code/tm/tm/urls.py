"""tm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf import settings
from django.urls import path
from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.core import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from django.conf.urls.static import static

urlpatterns = [
    path('cmsadmin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
    path('admin/', admin.site.urls),
    path('social-auth/',
         include('social_django.urls', namespace='social')),
]

urlpatterns += i18n_patterns(
    path('account/', include('account.urls')),
    path('', include(wagtail_urls)),
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
