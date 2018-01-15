import requests

from photo_object_classifier.ml_models import MODEL_VERSION


def classify_image(image):
    if image.photo_object_pred_v == MODEL_VERSION:
        return False
    if not image.image_big:
        return False
    resp = requests.post('http://localhost:9090/predict', data=image.image_big.read()).json()
    image.photo_object_pred = resp['class_index']
    image.photo_object_pred_v = resp['version']
    image.save(update_fields=['photo_object_pred', 'photo_object_pred_v'])
