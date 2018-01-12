import json

from django import template
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.safestring import mark_safe

from mobile_bg.utils import format_price

register = template.Library()


def _json_dumps_for_html(data):
    return json.dumps(data, ensure_ascii=False, cls=DjangoJSONEncoder)


@register.filter(is_safe=True)
def json_dumps(data):
    return mark_safe(_json_dumps_for_html(data))


@register.filter()
def any_ad_inactive(ads):
    for ad in ads:
        if not ad.active:
            return True
    return False


@register.filter()
def format_update_price(update):
    return format_price(update.price, update.price_currency)
