import requests
from django.core.management.base import BaseCommand
from requests import ConnectionError

from mobile_bg.models import MobileBgAdImage
from photo_object_classifier.api import classify_image


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            version = requests.get('http://localhost:9090/version').json()['version']
        except ConnectionError:
            print('ERROR: Unable to connect to prediction server!')
            exit(1)
        print('Listing images...')
        image_ids = list(MobileBgAdImage.objects.exclude(photo_object_pred_v=version).values_list(
            'id', flat=True))
        image_ids.sort()
        for i, image_id in enumerate(image_ids, 1):
            print('Classifying {} ({} / {})'.format(image_id, i, len(image_ids)))
            image = MobileBgAdImage.objects.get(id=image_id)
            classify_image(image)
