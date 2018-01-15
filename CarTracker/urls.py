"""CarTracker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin

import mobile_bg.urls
import ml_common.urls
import photo_object_classifier.urls
import photo_model_classifier.urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include(mobile_bg.urls, namespace='mobile_bg')),
    url(r'^ml/', include(
        ml_common.urls, namespace='ml_common')),
    url(r'^photo-object/', include(
        photo_object_classifier.urls, namespace='photo_object_classifier')),
    url(r'^photo-model/', include(
        photo_model_classifier.urls, namespace='photo_model_classifier')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
