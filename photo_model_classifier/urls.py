from django.conf.urls import url

from . import views

app_name = 'photo_model_classifier'

urlpatterns = [
    url(r'^demo$', views.DemoView.as_view(), name='demo'),
]
