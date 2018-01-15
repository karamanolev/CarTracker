from django.conf import settings

from ml_common.api import classify_image


def classify_image_photo_object(image):
    from mobile_bg.models import MobileBgAdImage
    class_name = classify_image(
        settings.PHOTO_OBJECT_MODEL_VERSION,
        9090,
        image,
    )
    return {
        'engine': MobileBgAdImage.PHOTO_OBJECT_ENGINE,
        'exterior': MobileBgAdImage.PHOTO_OBJECT_EXTERIOR,
        'interior': MobileBgAdImage.PHOTO_OBJECT_INTERIOR,
        'other': MobileBgAdImage.PHOTO_OBJECT_OTHER,
    }[class_name]


def save_image_photo_object_classification(image):
    image.photo_object_pred = classify_image_photo_object(image)
    image.photo_object_pred_v = settings.PHOTO_OBJECT_MODEL_VERSION
    image.save(update_fields=['photo_object_pred', 'photo_object_pred_v'])
