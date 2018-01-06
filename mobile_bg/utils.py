import json
import re

from CarTracker.utils import requests_get_retry


def parse_mobile_bg_price(raw_price):
    from mobile_bg.models import MobileBgAdUpdate
    raw_price = raw_price.replace(' ', '')
    if 'лв.' in raw_price:
        return int(raw_price.replace('лв.', '')), MobileBgAdUpdate.CURRENCY_BGN
    elif 'EUR' in raw_price:
        return int(raw_price.replace('EUR', '')), MobileBgAdUpdate.CURRENCY_EUR
    elif 'USD' in raw_price:
        return int(raw_price.replace('USD', '')), MobileBgAdUpdate.CURRENCY_USD
    else:
        raise Exception('Unknown currency for price {}'.format(raw_price))


def find_ga_prop(html, prop_name):
    pattern = (
            re.escape(".setTargeting('{}', ['".format(prop_name)) +
            "([^']*)" +
            re.escape("'])")
    )
    return re.search(pattern, html).group(1)


def _get_cmm_brands_models(data):
    return [{
        'name': item[0],
        'models': item[2:],
    } for item in data]


def get_cmm_vars():
    from mobile_bg.models import VehicleTypeMixin
    resp = requests_get_retry('https://www.mobile.bg/jss/cmmvars.js')
    text = resp.content.decode('windows-1251')
    m = re.search('var cmm = new Array\n\((.*?)\n\);\n', text, re.DOTALL)
    data = json.loads('[' + m.group(1).replace("'", '"') + ']')
    result = {
        'brands': {
            VehicleTypeMixin.VEHICLE_TYPE_CAR: _get_cmm_brands_models(data[0]),
            VehicleTypeMixin.VEHICLE_TYPE_SUV: _get_cmm_brands_models(data[1]),
            VehicleTypeMixin.VEHICLE_TYPE_VAN: _get_cmm_brands_models(data[2]),
            VehicleTypeMixin.VEHICLE_TYPE_TRUCK: _get_cmm_brands_models(data[3]),
            VehicleTypeMixin.VEHICLE_TYPE_MOTORCYCLE: _get_cmm_brands_models(data[4]),
        }
    }
    return result
