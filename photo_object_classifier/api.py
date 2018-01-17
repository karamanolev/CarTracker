from django.conf import settings

from ml_common.api import classify_image, classify_blob, SkipClassification

PORT = 9090


def _decode(class_name):
    from mobile_bg.models import MobileBgAdImage
    return {
        'engine': MobileBgAdImage.PHOTO_OBJECT_ENGINE,
        'exterior': MobileBgAdImage.PHOTO_OBJECT_EXTERIOR,
        'interior': MobileBgAdImage.PHOTO_OBJECT_INTERIOR,
        'other': MobileBgAdImage.PHOTO_OBJECT_OTHER,
    }[class_name]


def classify_blob_photo_object(blob):
    class_name = classify_blob(settings.PHOTO_OBJECT_MODEL_VERSION, PORT, blob)
    return _decode(class_name)


def classify_image_photo_object(image):
    class_name = classify_image(settings.PHOTO_OBJECT_MODEL_VERSION, PORT, image)
    return _decode(class_name)


def save_image_photo_object_classification(image):
    try:
        image.photo_object_pred = classify_image_photo_object(image)
        image.photo_object_pred_v = settings.PHOTO_OBJECT_MODEL_VERSION
        image.save(update_fields=['photo_object_pred', 'photo_object_pred_v'])
    except SkipClassification:
        print('Skipped image {}'.format(image.id))
