from django.conf.urls import url

from app import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^file_upload$', views.file_upload, name='file_upload'),
]