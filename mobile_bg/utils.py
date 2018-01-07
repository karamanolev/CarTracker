import json
import re
from datetime import date

from bs4 import NavigableString

from CarTracker.utils import requests_get_retry
from mobile_bg.models_mixins import EngineTypeMixin, TransmissionTypeMixin


def parse_price(raw_price):
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


def _get_contacts_table(bs):
    return bs.find(name='div', text='За контакти:').next_sibling.next_sibling


def parse_ad_location(bs):
    contacts_table = _get_contacts_table(bs)
    for e in contacts_table.descendants:
        if type(e) is NavigableString:
            t = str(e).strip()
            if t.startswith('Регион:'):
                t = t[len('Регион:'):].strip().split(',')
                assert 1 <= len(t) <= 2
                region = t[0].strip()
                city = None if len(t) < 2 else t[1].strip()
                return region, city
    raise Exception('Ad location not found')


def parse_ad_model_name_mod(bs):
    raw_name = bs.find(style='font-size:18px; font-weight:bold;')
    raw_name_children = list(raw_name.children)
    model_name = None
    model_mod = None
    if len(raw_name_children) >= 1:
        model_name = str(raw_name_children[0]).strip()
    if len(raw_name_children) >= 2:
        model_mod = raw_name_children[1].text.strip()
    return model_name, model_mod


def get_info_row(bs, title):
    title_el = bs.find(text=title)
    if title_el is None:
        return None
    return title_el.parent.next_sibling.text


def parse_ad_registration_date(bs):
    reg_date_row = get_info_row(bs, 'Дата на производство')
    if reg_date_row:
        reg_date_parts = reg_date_row.split()
        month = ['януари', 'февруари', 'март', 'април', 'май', 'юни', 'юли', 'август',
                 'септември', 'октомври', 'ноември', 'декември'].index(reg_date_parts[0]) + 1
        year = int(reg_date_parts[1])
        assert len(reg_date_parts) == 3
        assert reg_date_parts[2] == 'г.'
        return date(year, month, 1)
    return None


def parse_ad_engine_type(bs):
    engine_type_row = get_info_row(bs, 'Тип двигател')
    if engine_type_row:
        return {
            'Бензинов': EngineTypeMixin.ENGINE_PETROL,
            'Дизелов': EngineTypeMixin.ENGINE_DIESEL,
            'Хибриден': EngineTypeMixin.ENGINE_HYBRID,
            'Електрически': EngineTypeMixin.ENGINE_ELECTRIC,
        }[engine_type_row]
    return None


def parse_ad_mileage_km(bs):
    mileage_row = get_info_row(bs, 'Пробег')
    if mileage_row:
        mileage_parts = mileage_row.split()
        assert mileage_parts[1] == 'км'
        return int(mileage_parts[0])
    return None


def parse_ad_power_hp(bs):
    power_row = get_info_row(bs, 'Мощност')
    if power_row:
        power_parts = power_row.split()
        assert power_parts[1] == 'к.с.'
        return int(power_parts[0])
    return None


def parse_ad_transmission_type(bs):
    transmission_type_row = get_info_row(bs, 'Скоростна кутия')
    if transmission_type_row:
        return {
            'Ръчна': TransmissionTypeMixin.TRANSMISSION_MANUAL,
            'Автоматична': TransmissionTypeMixin.TRANSMISSION_AUTOMATIC,
            'Полуавтоматична': TransmissionTypeMixin.TRANSMISSION_SEMIAUTOMATIC,
        }[transmission_type_row]
    return None


def parse_ad_seller_name(bs):
    contacts_table = _get_contacts_table(bs)
    for e in contacts_table.descendants:
        if type(e) is NavigableString:
            t = str(e).strip()
            if t == 'Частно лице':
                return 'Частно лице'
    el = contacts_table.find(name='span', style='font-size:14px; font-weight:bold;')
    if el:
        return el.text.strip()
    return None
