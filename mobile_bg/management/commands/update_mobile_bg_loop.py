import traceback
from time import sleep, time

from django.conf import settings
from django.core.management import BaseCommand
from django.utils import timezone

from mobile_bg.scraper import scrape, print_ads_stats


class Command(BaseCommand):
    def execute(self, *args, **options):
        run_at = time()
        while True:
            sleep(max(0, run_at - time()))
            run_at += 43200  # 12 hours

            try:
                print('Start update at {}'.format(
                    timezone.now().astimezone(settings.TZ).strftime('%Y-%m-%d %H:%M:%S')))
                scrape()
                print_ads_stats()
            except Exception:
                traceback.print_exc()
