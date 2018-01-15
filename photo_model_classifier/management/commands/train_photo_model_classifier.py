from django.core.management.base import BaseCommand

from ml_common.training import train_model
from photo_model_classifier.ml_models import PMC_BASE_DIR, PMC_NUM_CLASSES, PMC_SAVED_MODEL_PATH


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('steps_per_epoch', type=int, default=1024)
        parser.add_argument('epochs', type=int, default=20)

    def handle(self, *args, **options):
        train_model(
            PMC_BASE_DIR,
            PMC_NUM_CLASSES,
            PMC_SAVED_MODEL_PATH,
            options['steps_per_epoch'],
            options['epoch'],
        )
