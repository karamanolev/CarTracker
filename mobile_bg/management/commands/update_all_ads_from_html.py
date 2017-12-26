from django.core.management.base import BaseCommand

from mobile_bg.models import MobileBgAdUpdate


class Command(BaseCommand):
    def handle(self, *args, **options):
        ids = list(MobileBgAdUpdate.objects.all().values_list('id', flat=True))
        for i, ad_id in enumerate(ids):
            print('{} / {}'.format(i, len(ids)))
            ad = MobileBgAdUpdate.objects.get(id=ad_id)
            ad.update_from_html(ad.html)
            ad.save()
