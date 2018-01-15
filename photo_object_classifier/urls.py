from django.conf.urls import url

from . import views

app_name = 'photo_object_classifier'

urlpatterns = [
    url(r'^annotate$', views.annotate, name='annotate'),
    url(r'^annotate-stats$', views.annotate_stats, name='annotate_stats'),
    url(r'^demo$', views.DemoView.as_view(), name='demo'),
]
