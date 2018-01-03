from django.core.management.base import BaseCommand
from django.db.models import Count

from CarTracker.utils import batch
from mobile_bg.models import MobileBgAd


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('Scanning...')
        ad_ids = list(
            MobileBgAd.objects
                .filter(last_active_update__isnull=False)
                .annotate(num_images=Count('images'))
                .order_by('num_images', '-last_full_update__date')
                .values_list('id', flat=True)
        )
        processed = 0
        for ids_batch in batch(ad_ids, 100):
            ads = MobileBgAd.objects.filter(id__in=ids_batch).select_related('last_active_update')
            for ad in ads:
                print('Processing {}'.format(ad.adv))
                ad.download_images()
                processed += 1
                print('{} / {}'.format(processed, len(ad_ids)))
