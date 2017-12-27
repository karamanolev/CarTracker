import traceback
from time import sleep

from django.core.management import BaseCommand

from mobile_bg.scraper import scrape, print_ads_stats


class Command(BaseCommand):
    def execute(self, *args, **options):
        while True:
            try:
                scrape()
                print_ads_stats()
            except Exception:
                traceback.print_exc()
            sleep(2)
