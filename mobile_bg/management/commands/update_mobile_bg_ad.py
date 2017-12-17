from django.core.management.base import BaseCommand

from mobile_bg.models import MobileBgAd


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('adv')

    def handle(self, *args, **options):
        ad = MobileBgAd.objects.get(adv=options['adv'])
        ad.update()
