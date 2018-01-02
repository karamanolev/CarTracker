import os

from django.conf import settings
from django.core.management.base import BaseCommand

from CarTracker.utils import batch
from mobile_bg.models import MobileBgAdImage, _image_big_upload_to


class Command(BaseCommand):
    def handle(self, *args, **options):
        total = 0
        renamed = 0
        skipped = 0
        ok = 0

        print('Scanning...')
        ids = MobileBgAdImage.objects.all().values_list('id', flat=True)
        for ids_batch in batch(ids, 1000):
            images = MobileBgAdImage.objects.filter(id__in=ids_batch).select_related('ad')
            for item in images:
                total += 1
                if not item.image_big.name:
                    skipped += 1
                    continue

                original_filename = '{}.jpg'.format(item.index)
                new_rel_path = _image_big_upload_to(item, original_filename)
                old_abs_path = os.path.join(settings.MEDIA_ROOT, item.image_big.name)
                new_abs_path = os.path.join(settings.MEDIA_ROOT, new_rel_path)

                if new_rel_path != item.image_big.name:
                    if os.path.isfile(new_abs_path) or not os.path.isfile(old_abs_path):
                        raise Exception('New exists or old missing; old="{}" new="{}"'.format(
                            old_abs_path, new_abs_path))
                    item.image_big.name = new_rel_path
                    item.save()
                    os.rename(old_abs_path, new_abs_path)
                    renamed += 1
                else:
                    ok += 1

                if total % 100 == 0:
                    print('Total: {}'.format(total))
                    print('Renamed: {}'.format(renamed))
                    print('Skipped: {}'.format(skipped))
                    print('OK: {}'.format(ok))
                    print()
