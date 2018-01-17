import os

from django.conf import settings
from django.utils.text import slugify

PMC_CLASSES = sorted([
    'Audi',
    'BMW',
    'Citroen',
    'Ford',
    'Mercedes-Benz',
    'Nissan',
    'Opel',
    'Peugeot',
    'Toyota',
    'VW',
])
PMC_NUM_CLASSES = len(PMC_CLASSES)
PMC_BASE_DIR = os.path.join(settings.BASE_DIR, 'photo_model_classifier')
PMC_SAVED_MODEL_PATH = os.path.join(PMC_BASE_DIR, 'saved_model.h5')

BRAND_TO_SLUG = {i: slugify(i) for i in PMC_CLASSES}
SLUG_TO_BRAND = {v: k for v, k in BRAND_TO_SLUG.items()}
