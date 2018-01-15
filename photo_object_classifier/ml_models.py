import os

from django.conf import settings

POC_NUM_CLASSES = 4
POC_BASE_DIR = os.path.join(settings.BASE_DIR, 'photo_object_classifier')
POC_SAVED_MODEL_PATH = os.path.join(POC_BASE_DIR, 'saved_model.h5')
POC_CLASSES = sorted(['interior', 'exterior', 'engine', 'other'])
