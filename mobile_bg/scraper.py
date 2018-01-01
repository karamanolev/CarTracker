from datetime import timedelta

from bs4 import BeautifulSoup
from django.db import transaction
from django.db.models.query_utils import Q
from django.utils import timezone

from mobile_bg.api import get_search_page
from mobile_bg.models import MobileBgAd, MobileBgAdUpdate, MobileBgScrapeLink


def _update_ads_list(scrape_link):
    page = 1
    ad_count = 0

    while True:
        with transaction.atomic():
            print('Fetching page {}'.format(page))
            text = get_search_page('3', scrape_link.slink, page)
            bs = BeautifulSoup(text, 'html.parser')
            els = bs.find_all(attrs={'class': 'mmm'})
            if not els:
                print('Zero results on page {}'.format(page))
                break
            for el in els:
                link = el['href']
                ad = MobileBgAd.from_url(link)
                if not ad.active:
                    ad.active = True
                    ad.save()
                if ad.last_full_update:
                    ad.update_partial(el)
                ad_count += 1
            bs.decompose()
            page += 1

    scrape_link.ad_count = ad_count
    scrape_link.last_update_date = timezone.now()
    scrape_link.save(update_fields=['ad_count', 'last_update_date'])


def _update_ad(ad):
    with transaction.atomic():
        last_update = None
        if ad.last_update:
            last_update = ad.last_update.date
        print('Updating {} (last update {})'.format(ad.adv, last_update))
        ad.update()


def _update_ads_by_id(ids):
    for i, ad_id in enumerate(ids):
        ad = MobileBgAd.objects.get(id=ad_id)
        _update_ad(ad)
        print('Done {}/{}'.format(i + 1, len(ids)))


def scrape():
    slink_threshold = timezone.now() - timedelta(hours=12)
    partial_threshold = timezone.now() - timedelta(hours=16)
    full_threshold = timezone.now() - timedelta(hours=48)

    scrape_links = MobileBgScrapeLink.objects.filter(
        Q(last_update_date__lte=slink_threshold) | Q(last_update_date=None),
    )
    for scrape_link in scrape_links:
        print('Updating slink {}: {}'.format(scrape_link.slink, scrape_link.name))
        _update_ads_list(scrape_link)

    ad_ids = list(MobileBgAd.objects.filter(
        Q(last_update=None) |
        Q(last_update__date__lte=partial_threshold, active=True) |
        Q(last_full_update__date__lte=full_threshold, active=True),
    ).values_list('id', flat=True)[:100])
    _update_ads_by_id(ad_ids)


def print_ads_stats():
    print('Number of ads: {}'.format(MobileBgAd.objects.count()))
    print('Number of active ads: {}'.format(
        MobileBgAd.objects.filter(last_update__active=True).count()))
    print('Number of ad updates: {}'.format(MobileBgAdUpdate.objects.count()))
    print('---------------------')
