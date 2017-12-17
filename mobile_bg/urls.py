from django.conf.urls import url

from .views import ad_data

urlpatterns = [
    url(r'^mobile-bg/ads/(\d+)$', ad_data),
]
