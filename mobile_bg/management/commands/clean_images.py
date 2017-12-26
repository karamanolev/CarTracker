import os

from django.conf import settings
from django.core.management.base import BaseCommand

from mobile_bg.models import MobileBgAdImage


class Command(BaseCommand):
    def handle(self, *args, **options):
        files = set()
        for item in MobileBgAdImage.objects.all().values_list('image_small', 'image_big'):
            for i in item:
                files.add(i)

        removed = set()
        matched = set()

        def _process_file(rel_path):
            if rel_path in files:
                matched.add(rel_path)
            else:
                removed.add(rel_path)

        for dirpath, dirnames, filenames in os.walk(settings.MEDIA_ROOT):
            for filename in filenames:
                abs_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(abs_path, settings.MEDIA_ROOT)
                _process_file(rel_path)

        print('Matched:', len(matched))
        print('Removed:', len(removed))
        if len(removed) and input('Proceed (y/n): ') == 'y':
            for rel_path in removed:
                abs_path = os.path.join(settings.MEDIA_ROOT, rel_path)
                print('Deleting', abs_path)
                os.remove(abs_path)
