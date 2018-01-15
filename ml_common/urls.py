from django.conf.urls import url

from . import views

app_name = 'ml_common'

urlpatterns = [
    url(r'^demo$', views.DemoView.as_view(), name='demo'),
]
