from django.core.management.base import BaseCommand

from mobile_bg.models import MobileBgAdUpdate, MobileBgAd


class Command(BaseCommand):
    def handle(self, *args, **options):
        ad_ids = list(MobileBgAd.objects.all().values_list('id', flat=True))
        for i, ad_id in enumerate(ad_ids):
            updates = list(MobileBgAdUpdate.objects.filter(ad_id=ad_id).order_by('date'))
            for up in updates:
                up.try_compress()
                up.save()
            print('{} / {} ({})'.format(i + 1, len(ad_ids), len(updates)))
