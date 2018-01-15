from django.conf import settings
from django.core.management import BaseCommand

from ml_common.prediction_server import PredictionServer
from photo_model_classifier.ml_models import PMC_SAVED_MODEL_PATH, PMC_CLASSES


class Command(BaseCommand):
    def handle(self, *args, **options):
        server = PredictionServer(
            PMC_SAVED_MODEL_PATH,
            settings.PHOTO_MODEL_MODEL_VERSION,
            PMC_CLASSES,
        )
        server.serve(9091)
