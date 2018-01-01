from time import sleep
from urllib.parse import urlencode

from django.conf import settings

from CarTracker.utils import requests_get_retry


def get_search_page(act, slink, page):
    resp = requests_get_retry('https://www.mobile.bg/pcgi/mobile.cgi?{}'.format(
        urlencode({
            'act': str(act),
            'slink': slink,
            'f1': str(page),
        })))
    sleep(settings.REQUEST_DELAY)
    return resp.content.decode('windows-1251')
