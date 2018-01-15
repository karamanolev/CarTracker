import requests
from django.conf import settings


def classify_image(image):
    from mobile_bg.models import MobileBgAdImage
    if image.photo_object_pred_v == settings.PHOTO_OBJECT_MODEL_VERSION:
        return False
    if not image.image_big:
        return False
    data = image.image_big.read()
    if len(data) == 0:
        return False
    resp = requests.post('http://localhost:9090/predict', data=data).json()
    if resp['version'] != settings.PHOTO_OBJECT_MODEL_VERSION:
        raise Exception('Incosistent codebase and server versions')
    image.photo_object_pred = {
        'engine': MobileBgAdImage.PHOTO_OBJECT_ENGINE,
        'exterior': MobileBgAdImage.PHOTO_OBJECT_EXTERIOR,
        'interior': MobileBgAdImage.PHOTO_OBJECT_INTERIOR,
        'other': MobileBgAdImage.PHOTO_OBJECT_OTHER,
    }[resp['class_name']]
    image.photo_object_pred_v = resp['version']
    image.save(update_fields=['photo_object_pred', 'photo_object_pred_v'])
