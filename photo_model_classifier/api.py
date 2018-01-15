from django.conf import settings

from ml_common.api import classify_image, classify_blob

PORT = 9091


def classify_blob_photo_model(blob):
    return classify_blob(settings.PHOTO_MODEL_MODEL_VERSION, PORT, blob)


def classify_image_photo_model(image):
    return classify_image(settings.PHOTO_MODEL_MODEL_VERSION, PORT, image)
