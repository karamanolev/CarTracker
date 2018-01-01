from django.core.management.base import BaseCommand

from mobile_bg.models import MobileBgAd, MobileBgScrapeLink


class Command(BaseCommand):
    def handle(self, *args, **options):
        for scrape_link in MobileBgScrapeLink.objects.all():
            print('Verifying {}'.format(scrape_link.slink))
            scrape_link.verify()
