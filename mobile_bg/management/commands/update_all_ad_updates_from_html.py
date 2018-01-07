from random import shuffle

from django.core.management.base import BaseCommand
from django.db import transaction

from mobile_bg.models import MobileBgAdUpdate, MobileBgAd


class Command(BaseCommand):
    def handle(self, *args, **options):
        ad_ids = list(MobileBgAd.objects.all().values_list('id', flat=True))
        shuffle(ad_ids)
        for i, ad_id in enumerate(ad_ids):
            with transaction.atomic():
                updates = list(MobileBgAdUpdate.objects.filter(
                    ad_id=ad_id).order_by('date'))
                updates_by_id = {u.id: u for u in updates}
                updates_by_id[None] = None
                for up in updates:
                    up.prev_update = updates_by_id[up.prev_update_id]

                for up in updates:
                    print('Processing update id {}'.format(up.id))
                    up.update_from_html()
                    up.save()

                print('{} / {} ({})'.format(i + 1, len(ad_ids), len(updates)))
