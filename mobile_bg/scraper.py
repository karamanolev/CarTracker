from datetime import timedelta

from bs4 import BeautifulSoup
from django.db import transaction
from django.db.models.query_utils import Q
from django.utils import timezone

from mobile_bg.api import get_search_page, get_home_page
from mobile_bg.models import MobileBgAd, MobileBgAdUpdate, MobileBgScrapeLink


def _update_ads_list(scrape_link):
    page = 1
    ad_count = 0

    while True:
        with transaction.atomic():
            print('Fetching page {}'.format(page))
            text = get_search_page('3', scrape_link.slink, page)
            bs = BeautifulSoup(text, 'html5lib')
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
        if ad.last_full_update:
            last_update = ad.last_full_update.date
        print('Updating {} (last full update {})'.format(ad.adv, last_update))
        ad.update()


def _update_ads_by_id(ids):
    for i, ad_id in enumerate(ids):
        ad = MobileBgAd.objects.get(id=ad_id)
        _update_ad(ad)
        print('Done {}/{}'.format(i + 1, len(ids)))


def scrape():
    slink_threshold = timezone.now() - timedelta(hours=12)
    partial_threshold = timezone.now() - timedelta(hours=16)
    full_threshold = timezone.now() - timedelta(hours=72)

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


def verify_slinks():
    print('Verifying makes')
    resp = get_home_page()
    bs = BeautifulSoup(resp, 'html5lib')
    brands = {i.text.strip() for i in bs.find(attrs={'name': 'marka'}).find_all(name='option')
              if i.text != 'всички\n'}
    scrape_links = list(MobileBgScrapeLink.objects.all())
    scrape_brands = {i.name for i in scrape_links}
    missing_brands = brands - scrape_brands
    extra_brands = brands - scrape_brands
    if missing_brands:
        raise Exception('Brands {} is missing a link!'.format(', '.join(sorted(missing_brands))))
    if extra_brands:
        raise Exception('Brands {} is no longer found!'.format(', '.join(sorted(missing_brands))))

    print('Verifying ranges')
    for brand in brands:
        brand_links = [i for i in scrape_links if i.name == brand]
        if not brand_links:
            raise Exception('No brand links for {}'.format(brand))
        if brand_links[0].min_price is not None:
            raise Exception('Invalid first min_price for {}'.format(brand))
        if brand_links[-1].max_price is not None:
            raise Exception('Invalid last max_price for {}'.format(brand))
        for i in range(1, len(brand_links)):
            if brand_links[i].min_price != brand_links[i - 1].max_price:
                raise Exception('Invalid min_price for {} on {}'.format(brand, i))

    for scrape_link in scrape_links:
        print('Verifying {}'.format(scrape_link.slink))
        scrape_link.verify()
