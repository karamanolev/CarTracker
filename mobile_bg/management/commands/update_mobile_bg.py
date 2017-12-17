from django.core.management.base import BaseCommand

from mobile_bg.scraper import scrape, print_ads_stats


class Command(BaseCommand):
    def handle(self, *args, **options):
        scrape()
        print_ads_stats()
