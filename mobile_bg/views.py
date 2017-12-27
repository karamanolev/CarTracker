import json

from django.http.response import Http404, HttpResponse
from django.shortcuts import render

from CarTracker.utils import json_serialize
from mobile_bg.models import MobileBgAd, MobileBgAdImage


def ad_data(request, adv):
    try:
        ad = MobileBgAd.objects.get(adv=adv)
    except MobileBgAd.DoesNotExist:
        raise Http404()

    filtered = ad.get_filtered_updates()

    response = HttpResponse(
        json.dumps({
            'added': ad.first_update.date,
            'url': ad.url,
            'updates': [{
                'date': i.date,
                'price': i.price,
            } for i in filtered],
        }, default=json_serialize),
        content_type='application/json',
    )
    response['Access-Control-Allow-Origin'] = '*'
    return response


def ad_image(request, adv, index, size):
    try:
        ad_image = MobileBgAdImage.objects.get(ad__adv=adv, index=index)
    except MobileBgAdImage.DoesNotExist:
        raise Http404()

    if size == 'big':
        result = ad_image.image_big.read()
    elif size == 'small':
        result = ad_image.image_small.read()
    else:
        raise Http404()

    return HttpResponse(result, content_type='image/jpeg')


def index(request):
    return render(request, 'mobile_bg/index.html', {
        'last_price_changes': MobileBgAd.get_recent_price_changes()[:5],
        'last_unlists': MobileBgAd.get_recent_unlists()[:5],
    })


def recent_price_changes(request):
    return render(request, 'mobile_bg/recent_price_changes.html', {
        'ads': MobileBgAd.get_recent_price_changes()[:100],
    })



def recent_unlists(request):
    return render(request, 'mobile_bg/recent_unlists.html', {
        'ads': MobileBgAd.get_recent_unlists()[:100],
    })
