import json
import traceback
from datetime import date, datetime
from time import sleep

import requests
from django.conf import settings
from django.http import HttpResponse
from requests import RequestException


class HttpNotFoundException(RequestException):
    def __init__(self, response):
        self.response = response


def json_serialize(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def requests_get_retry(url, params=None):
    retries_left = settings.REQUEST_RETRY_COUNT
    while True:
        try:
            resp = requests.get(
                url,
                params=params,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36'
                                  ' (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
                },
                timeout=30,
            )
            resp.raise_for_status()
            if retries_left != settings.REQUEST_RETRY_COUNT:
                print('Retrying succeeded...')
            return resp
        except (ConnectionError, RequestException) as ex:
            response = getattr(ex, 'response')
            if response is not None and response.status_code == 404:
                raise HttpNotFoundException(response)

            retries_left -= 1
            if not retries_left:
                raise
            sleep(settings.REQUEST_RETRY_TIMEOUT)
            traceback.print_exc()
            print('Requesting {} failed, retrying...'.format(url))


def batch(iterable, n):
    current_batch = []
    for i in iterable:
        current_batch.append(i)
        if len(current_batch) >= n:
            yield current_batch
            current_batch = []
    if current_batch:
        yield current_batch


def json_response(data):
    response = HttpResponse(
        json.dumps(data, default=json_serialize),
        content_type='application/json',
    )
    response['Access-Control-Allow-Origin'] = '*'
    return response
