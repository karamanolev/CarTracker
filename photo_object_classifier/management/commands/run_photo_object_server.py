from django.conf import settings
from django.core.management import BaseCommand

from ml_common.prediction_server import PredictionServer
from photo_object_classifier.ml_models import POC_SAVED_MODEL_PATH, POC_CLASSES


class Command(BaseCommand):
    def handle(self, *args, **options):
        server = PredictionServer(
            POC_SAVED_MODEL_PATH,
            settings.PHOTO_OBJECT_MODEL_VERSION,
            POC_CLASSES,
        )
        server.serve(9090)
