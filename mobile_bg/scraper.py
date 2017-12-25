from time import sleep
from urllib.parse import urlencode

from bs4 import BeautifulSoup
from django.conf import settings
from django.db import transaction

from CarTracker.utils import requests_get_retry
from mobile_bg.models import MobileBgAd, MobileBgAdUpdate

SCRAPE_SLINKS = {
    '5m8424': 'Electric Cars',
    '5jtd4b': 'BMW >= 2007, >= 14000 leva',
    '5jtdag': 'Audi >= 2007, >= 14000 leva',
}


def _update_ads_list(slink):
    page = 1

    while True:
        print('Fetching page {}'.format(page))
        resp = requests_get_retry('https://www.mobile.bg/pcgi/mobile.cgi?{}'.format(
            urlencode({
                'act': '3',
                'slink': slink,
                'f1': str(page),
            })))
        text = resp.content.decode('windows-1251')
        bs = BeautifulSoup(text, 'html.parser')
        els = bs.find_all(attrs={'class': 'mmm'})
        if not els:
            print('Zero results on page {}'.format(page))
            break
        for el in els:
            link = el['href']
            with transaction.atomic():
                ad = MobileBgAd.from_url(link)
                if not ad.active:
                    ad.active = True
                    ad.save()
        bs.decompose()
        sleep(settings.REQUEST_DELAY)
        page += 1


def _update_ad(ad):
    with transaction.atomic():
        last_update = None
        if ad.last_update:
            last_update = ad.last_update.date
        print('Updating {} (last update {})'.format(ad.adv, last_update))
        ad.update()
    sleep(settings.REQUEST_DELAY)


def _update_ads_by_id(ids):
    for i, ad_id in enumerate(ids):
        ad = MobileBgAd.objects.get(id=ad_id)
        _update_ad(ad)
        print('Done {}/{}'.format(i + 1, len(ids)))


def _update_ads():
    never_updated_ids = list(
        MobileBgAd.objects.filter(last_update=None).order_by('adv').values_list(
            'id', flat=True))
    updated_ids = list(
        MobileBgAd.objects.filter(active=True).exclude(last_update=None).order_by(
            'last_update__date', 'adv').values_list('id', flat=True))

    _update_ads_by_id(never_updated_ids + updated_ids)


def scrape():
    for slink, name in SCRAPE_SLINKS.items():
        print('Updating slink {}: {}'.format(slink, name))
        _update_ads_list(slink)
    _update_ads()


def print_ads_stats():
    print('Number of ads: {}'.format(MobileBgAd.objects.count()))
    print('Number of active ads: {}'.format(
        MobileBgAd.objects.filter(last_update__active=True).count()))
    print('Number of ad updates: {}'.format(MobileBgAdUpdate.objects.count()))
