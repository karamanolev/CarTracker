import json

from django.http.response import Http404, HttpResponse
from django.shortcuts import render

from CarTracker.utils import json_serialize
from mobile_bg.models import MobileBgAd


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


def home(request):
    return render(request, 'index.html')
