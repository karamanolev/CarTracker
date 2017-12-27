from django.core.management.base import BaseCommand

from mobile_bg.models import MobileBgAd


class Command(BaseCommand):
    def handle(self, *args, **options):
        ids = list(MobileBgAd.objects.all().values_list('id', flat=True))
        for i, ad_id in enumerate(ids):
            print('{} / {}'.format(i, len(ids)))
            ad = MobileBgAd.objects.get(id=ad_id)
            ad.update_computed_fields()
            ad.save()
