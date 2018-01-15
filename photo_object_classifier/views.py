from django.shortcuts import render
from django.utils import timezone

from ml_common.views import DemoViewBase
from mobile_bg.models import MobileBgAdImage
from photo_object_classifier.api import classify_blob_photo_object


def annotate(request):
    if request.method == 'POST':
        if 'whoops' in request.POST:
            annotated_image = MobileBgAdImage.objects.filter(
                photo_object_at__isnull=False).order_by('-photo_object_at').first()
            annotated_image.photo_object = None
            annotated_image.photo_object_at = None
        else:
            annotated_image = MobileBgAdImage.objects.get(id=request.POST['image_id'])
            annotated_image.photo_object = int(request.POST['photo_object'])
            annotated_image.photo_object_at = timezone.now()
        annotated_image.save(update_fields=['photo_object', 'photo_object_at'])

    images = MobileBgAdImage.objects.filter(image_big__isnull=False, photo_object=None).order_by(
        'id').select_related('ad')[:3]
    prev_images = MobileBgAdImage.objects.filter(
        photo_object_at__isnull=False).order_by('-photo_object_at')[:2]
    return render(request, 'photo_object_classifier/annotate.html', {
        'image': images[0],
        'next_images': images[1:],
        'prev_images': prev_images,
    })


def annotate_stats(request):
    return render(request, 'photo_object_classifier/annotate_stats.html', {
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


class DemoView(DemoViewBase):
    def get_class_display(self, image_data):
        return [MobileBgAdImage.photo_object_to_str(classify_blob_photo_object(image_data))]
