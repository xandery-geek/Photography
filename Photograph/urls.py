"""Photograph URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.views.generic.base import TemplateView
from django.conf.urls.static import static

from Photograph import settings
from album.views import AlbumView, ImageList, ImageDetail, OperationView

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
                  re_path(r'^$', AlbumView.as_view(), name='index'),
                  re_path(r'^(?P<category>[-\w]+)$', AlbumView.as_view(), name='album'),
                  re_path(r'^album/(?P<album_id>[\d]+)/page/(?P<page>[\d]+)$', ImageList.as_view(),
                          name='album_detail'),
                  re_path(r'^image/(?P<image_id>[\d]+)$', ImageDetail.as_view(), name='image_detail'),
                  re_path(r'^image/(?P<option>[\w]+)/(?P<image_id>[\w]+)$', OperationView.as_view(),
                          name="image_operate"),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'album.views.handler404'
