from django.conf.urls import url

from .views import ad_data, ad_image, index

app_name = 'mobile_bg'

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^mobile-bg/ads/(\d+)$', ad_data, name='ad_data'),
    url(r'^mobile-bg/ads/(\d+)/images/(\d+)/(big|small)$', ad_image, name='ad_image'),
]
