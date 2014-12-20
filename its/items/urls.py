from django.conf.urls import patterns, url

from its.items import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
)