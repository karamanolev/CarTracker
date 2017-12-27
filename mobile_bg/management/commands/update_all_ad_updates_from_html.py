from django.core.management.base import BaseCommand

from mobile_bg.models import MobileBgAdUpdate


class Command(BaseCommand):
    def handle(self, *args, **options):
        ids = list(MobileBgAdUpdate.objects.all().values_list('id', flat=True))
        for i, up_id in enumerate(ids):
            print('{} / {}'.format(i, len(ids)))
            up = MobileBgAdUpdate.objects.get(id=up_id)
            up.update_from_html()
            up.save()
