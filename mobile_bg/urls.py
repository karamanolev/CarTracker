from django.conf.urls import url

from .views import ad_data, ads_data, ad_image, index, recent_price_changes, recent_unlists

app_name = 'mobile_bg'

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^recent-price-changes$', recent_price_changes, name='recent_price_changes'),
    url(r'^recent-unlists$', recent_unlists, name='recent_unlists'),
    url(r'^mobile-bg/ads/(\d+)$', ad_data, name='ad_data'),
    url(r'^mobile-bg/ads/$', ads_data, name='ads_data'),
    url(r'^mobile-bg/ads/(\d+)/images/(\d+)/(big|small)$', ad_image, name='ad_image'),
]
