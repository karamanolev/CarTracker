from django.core.management.base import BaseCommand

from mobile_bg.scraper import verify_slinks


class Command(BaseCommand):
    def handle(self, *args, **options):
        verify_slinks()
