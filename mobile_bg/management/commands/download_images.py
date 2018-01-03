from django.core.management.base import BaseCommand
from django.db.models import Count

from mobile_bg.models import MobileBgAd


class Command(BaseCommand):
    def handle(self, *args, **options):
        ads = list(
            MobileBgAd.objects
                .filter(last_active_update__isnull=False)
                .annotate(num_images=Count('images'))
                .order_by('num_images', '-last_full_update__date')[:30000]
        )
        for i, ad in enumerate(ads):
            ad.download_images()
            print('{} / {}'.format(i + 1, len(ads)))
