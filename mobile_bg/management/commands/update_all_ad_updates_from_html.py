from django.core.management.base import BaseCommand
from django.db import transaction

from mobile_bg.models import MobileBgAdUpdate, MobileBgAd


class Command(BaseCommand):
    def handle(self, *args, **options):
        ad_ids = list(MobileBgAd.objects.all().values_list('id', flat=True))
        for i, ad_id in enumerate(ad_ids):
            with transaction.atomic():
                updates = list(MobileBgAdUpdate.objects.filter(
                    ad_id=ad_id).order_by('date'))
                for up in updates:
                    up.update_from_html()
                    up.save()
                print('{} / {} ({})'.format(i + 1, len(ad_ids), len(updates)))
