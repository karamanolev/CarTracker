import os

from django.conf import settings
from django.utils.text import slugify

BRANDS = ['Audi', 'BMW', 'Mercedes-Benz', 'VW']

PMC_NUM_CLASSES = len(BRANDS)
PMC_BASE_DIR = os.path.join(settings.BASE_DIR, 'photo_model_classifier')
PMC_SAVED_MODEL_PATH = os.path.join(PMC_BASE_DIR, 'saved_model.h5')

BRAND_TO_SLUG = {i: slugify(i) for i in BRANDS}

SLUG_TO_BRAND = {v: k for v, k in BRAND_TO_SLUG.items()}
