from datetime import date, datetime
from time import sleep

import requests
from django.conf import settings
from requests import RequestException


def json_serialize(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def requests_get_retry(url):
    retries_left = 3
    while True:
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            return resp
        except RequestException:
            retries_left -= 1
            if not retries_left:
                raise
            sleep(settings.REQUEST_RETRY_TIMEOUT)
            print('Requesting {} failed, retrying...'.format(url))
