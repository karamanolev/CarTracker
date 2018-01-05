import re


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
