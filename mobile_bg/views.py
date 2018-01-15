from django.http.response import Http404, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from CarTracker.utils import json_response
from mobile_bg.models import MobileBgAd, MobileBgAdImage
from mobile_bg.serializers import MobileBgAdSerializer


def ad_data(request, adv):
    try:
        ad = MobileBgAd.objects.get(adv=adv)
    except MobileBgAd.DoesNotExist:
        raise Http404()

    return json_response(MobileBgAdSerializer(ad).data)


def ads_data(request):
    advs = request.GET['advs'].split(',')
    ads = list(MobileBgAd.objects.filter(adv__in=advs))
    return json_response({ad.adv: MobileBgAdSerializer(ad).data for ad in ads})


def ad_image(request, adv, index, size):
    try:
        ad_image = MobileBgAdImage.objects.get(ad__adv=adv, index=index)
    except MobileBgAdImage.DoesNotExist:
        raise Http404()

    if size == 'big':
        result = ad_image.image_big.read()
    elif size == 'small':
        raise Http404()
    else:
        raise Http404()

    resp = HttpResponse(result, content_type='image/jpeg')
    resp['Cache-Control'] = 'public, max-age=86400'
    return resp


def index(request):
    return render(request, 'mobile_bg/index.html', {
        'last_price_changes': MobileBgAd.get_recent_price_changes()[:5],
        'last_unlists': MobileBgAd.get_recent_unlists()[:5],
    })


def recent_price_changes(request):
    return render(request, 'mobile_bg/recent_price_changes.html', {
        'ads': list(MobileBgAd.get_recent_price_changes().select_related(
            'last_active_update',
            'first_update',
        )[:100]),
    })


def recent_unlists(request):
    return render(request, 'mobile_bg/recent_unlists.html', {
        'ads': list(MobileBgAd.get_recent_unlists().select_related(
            'last_active_update',
            'first_update',
        )[:100]),
    })
