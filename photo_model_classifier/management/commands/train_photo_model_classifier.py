from django.core.management.base import BaseCommand

from ml_common.training import train_model
from photo_model_classifier.ml_models import PMC_BASE_DIR, PMC_NUM_CLASSES, PMC_SAVED_MODEL_PATH


class Command(BaseCommand):
    def handle(self, *args, **options):
        train_model(PMC_BASE_DIR, PMC_NUM_CLASSES, PMC_SAVED_MODEL_PATH, 512, 10)
