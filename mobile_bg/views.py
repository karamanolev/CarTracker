from django.db.models import F
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


def annotate_interior_exterior(request):
    if request.method == 'POST':
        if 'whoops' in request.POST:
            annotated_image = MobileBgAdImage.objects.order_by(
                F('photo_object_at').desc(nulls_last=True)).first()
            annotated_image.photo_object = None
            annotated_image.photo_object_at = None
        else:
            annotated_image = MobileBgAdImage.objects.get(id=request.POST['image_id'])
            annotated_image.photo_object = int(request.POST['photo_object'])
            annotated_image.photo_object_at = timezone.now()
        annotated_image.save(update_fields=['photo_object', 'photo_object_at'])

    image = MobileBgAdImage.objects.filter(image_big__isnull=False, photo_object=None).order_by(
        'id').select_related('ad').first()
    print(image.ad.adv)
    return render(request, 'mobile_bg/annotate_interior_exterior.html', {
        'image': image,
    })


def annotate_interior_exterior_stats(request):
    return render(request, 'mobile_bg/annotate_interior_exterior_stats.html', {
        'num_annotated': MobileBgAdImage.objects.filter(photo_object__isnull=False).count(),
        'num_not_annotated': MobileBgAdImage.objects.filter(photo_object__isnull=True).count(),
        'num_total': MobileBgAdImage.objects.count(),
        'num_exterior': MobileBgAdImage.objects.filter(
            photo_object=MobileBgAdImage.PHOTO_OBJECT_EXTERIOR).count(),
        'num_interior': MobileBgAdImage.objects.filter(
            photo_object=MobileBgAdImage.PHOTO_OBJECT_INTERIOR).count(),
        'num_engine': MobileBgAdImage.objects.filter(
            photo_object=MobileBgAdImage.PHOTO_OBJECT_ENGINE).count(),
        'num_other': MobileBgAdImage.objects.filter(
            photo_object=MobileBgAdImage.PHOTO_OBJECT_OTHER).count(),
    })
