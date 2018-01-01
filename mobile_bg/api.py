from time import sleep

from django.conf import settings

from CarTracker.utils import requests_get_retry


def _fetch_page(url, params=None):
    resp = requests_get_retry(url, params)
    sleep(settings.REQUEST_DELAY)
    return resp.content.decode('windows-1251')


def get_search_page(act, slink, page):
    return _fetch_page('https://www.mobile.bg/pcgi/mobile.cgi', {
        'act': str(act),
        'slink': slink,
        'f1': str(page),
    })


def get_home_page():
    return _fetch_page('https://www.mobile.bg/index_koli.html')
