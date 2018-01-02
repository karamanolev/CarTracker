import os

from django.conf import settings
from django.core.management.base import BaseCommand

from mobile_bg.models import MobileBgAdImage


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('Scanning database...')
        db_files = set()
        for item in MobileBgAdImage.objects.all().values_list('image_small', 'image_big'):
            for i in item:
                db_files.add(i)

        print('Scanning filesystem...')
        fs_files = set()
        for dirpath, dirnames, filenames in os.walk(settings.MEDIA_ROOT):
            for filename in filenames:
                abs_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(abs_path, settings.MEDIA_ROOT)
                fs_files.add(rel_path)

        matched = fs_files.intersection(db_files)
        removed = fs_files.difference(db_files)
        missing = db_files.difference(fs_files)
        print('Matched:', len(matched))
        print('Removed:', len(removed))
        print('Missing:', len(missing))
        if len(removed) and input('Proceed (y/n): ') == 'y':
            for rel_path in removed:
                abs_path = os.path.join(settings.MEDIA_ROOT, rel_path)
                print('Deleting', abs_path)
                os.remove(abs_path)
