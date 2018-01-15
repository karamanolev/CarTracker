from django.core.management.base import BaseCommand

from ml_common.training import train_model
from photo_object_classifier.ml_models import POC_NUM_CLASSES, POC_BASE_DIR, POC_SAVED_MODEL_PATH


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('steps_per_epoch', type=int, default=1024)
        parser.add_argument('epochs', type=int, default=20)

    def handle(self, *args, **options):
        train_model(
            POC_BASE_DIR,
            POC_NUM_CLASSES,
            POC_SAVED_MODEL_PATH,
            options['steps_per_epoch'],
            options['epoch'],
        )
