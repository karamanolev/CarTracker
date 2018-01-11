from django.conf.urls import url

from . import views

app_name = 'mobile_bg'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^recent-price-changes$', views.recent_price_changes, name='recent_price_changes'),
    url(r'^recent-unlists$', views.recent_unlists, name='recent_unlists'),
    url(r'^mobile-bg/ads/(\d+)$', views.ad_data, name='ad_data'),
    url(r'^mobile-bg/ads/$', views.ads_data, name='ads_data'),
    url(r'^mobile-bg/ads/(\d+)/images/(\d+)/(big|small)$', views.ad_image, name='ad_image'),
    url(r'^annotate-interior-exterior$', views.annotate_interior_exterior, name='annotate_interior_exterior'),
]
