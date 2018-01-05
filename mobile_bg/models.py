import hashlib
import json
import re
from datetime import date
from multiprocessing import dummy
from time import sleep
from urllib.parse import urlparse, parse_qs, urlencode

import bsdiff4
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models, transaction
from django.utils import timezone

from CarTracker.utils import requests_get_retry, HttpNotFoundException
from mobile_bg.api import get_search_page
from mobile_bg.utils import parse_mobile_bg_price


class ColorMixin(models.Model):
    COLORS = [
        'Tъмно син',
        'Банан',
        'Беата',
        'Бежов',
        'Бордо',
        'Бронз',
        'Бял',
        'Винен',
        'Виолетов',
        'Вишнев',
        'Графит',
        'Жълт',
        'Зелен',
        'Златист',
        'Кафяв',
        'Керемиден',
        'Кремав',
        'Лилав',
        'Металик',
        'Оранжев',
        'Охра',
        'Пепеляв',
        'Перла',
        'Пясъчен',
        'Резидав',
        'Розов',
        'Сахара',
        'Светло сив',
        'Светло син',
        'Сив',
        'Син',
        'Слонова кост',
        'Сребърен',
        'Т.зелен',
        'Тъмно сив',
        'Тъмно син мет.',
        'Тъмно червен',
        'Тютюн',
        'Хамелеон',
        'Червен',
        'Черен'
    ]

    color = models.IntegerField(null=True, blank=True)

    @classmethod
    def color_to_code(cls, color_name):
        return cls.COLORS.index(color_name)

    @classmethod
    def code_to_color(cls, color_code):
        return cls.COLORS[color_code]

    class Meta:
        abstract = True


class VehicleTypeMixin(models.Model):
    VEHICLE_TYPE_CAR = 1
    VEHICLE_TYPE_SUV = 2
    VEHICLE_TYPE_VAN = 3
    VEHICLE_TYPE_TRUCK = 4
    VEHICLE_TYPE_MOTORCYCLE = 5
    VEHICLE_TYPE_AGRICULTURAL = 6
    VEHICLE_TYPE_INDUSTRIAL = 7
    VEHICLE_TYPE_MOTORCAR = 8
    VEHICLE_TYPE_CARAVAN = 9
    VEHICLE_TYPE_BOAT = ord('a')
    VEHICLE_TYPE_TRAILER = ord('b')
    VEHICLE_TYPE_BIKE = ord('c')
    VEHICLE_TYPE_PARTS = ord('u')
    VEHICLE_TYPE_ACCESSORIES = ord('v')
    VEHICLE_TYPE_TYRES_AND_RIMS = ord('w')
    VEHICLE_TYPE_BUYING = ord('y')
    VEHICLE_TYPE_SERVICES = ord('z')

    VEHICLE_TYPE_CHOICES = (
        (VEHICLE_TYPE_CAR, 'Кола'),
        (VEHICLE_TYPE_SUV, 'Джип'),
        (VEHICLE_TYPE_VAN, 'Бус'),
        (VEHICLE_TYPE_TRUCK, 'Камион'),
        (VEHICLE_TYPE_MOTORCYCLE, 'Мотоциклет'),
        (VEHICLE_TYPE_AGRICULTURAL, 'Селскостопански'),
        (VEHICLE_TYPE_INDUSTRIAL, 'Индустриален'),
        (VEHICLE_TYPE_MOTORCAR, 'Кар'),
        (VEHICLE_TYPE_CARAVAN, 'Каравана'),
    )

    VEHICLE_TYPE_BY_MOBILE_BG_NAME = {
        'Автомобили': VEHICLE_TYPE_CAR,
        'Джипове': VEHICLE_TYPE_SUV,
        'Бусове': VEHICLE_TYPE_VAN,
        'Камиони': VEHICLE_TYPE_TRUCK,
        'Мотоциклети': VEHICLE_TYPE_MOTORCYCLE,
    }

    vehicle_type = models.IntegerField(choices=VEHICLE_TYPE_CHOICES)

    class Meta:
        abstract = True


class MobileBgScrapeLink(VehicleTypeMixin, models.Model):
    slink = models.CharField(max_length=16)
    name = models.CharField(max_length=64)
    min_price = models.IntegerField(null=True, blank=True)
    max_price = models.IntegerField(null=True, blank=True)
    last_update_date = models.DateTimeField(null=True, blank=True)
    ad_count = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ('name', 'max_price')

    def verify(self):
        text = get_search_page('3', self.slink, 1)
        bs = BeautifulSoup(text, 'html5lib')
        cell = bs.find(text='Резултат от Вашето търсене на:')
        search_text = cell.parent.parent.text
        search_text = search_text.strip()
        search_text = search_text.replace('Особености: ', '')
        if self.min_price and self.max_price:
            expected_price = 'Цена: от {} до {} лв., '.format(self.min_price, self.max_price)
        elif self.min_price:
            expected_price = 'Цена: от {} лв., '.format(self.min_price)
        elif self.max_price:
            expected_price = 'Цена: до {} лв., '.format(self.max_price)
        else:
            expected_price = ''
        expected_text = (
            'Резултат от Вашето търсене на:'
            '\n            Рубрика: Автомобили, {}; Състояние: Употребявани, Нови, '
            '{}'
            'Подредени по: Марка/Модел/Цена'
        ).format(
            self.name,
            expected_price,
        )
        if search_text != expected_text:
            raise Exception('Slink {} does not verify "{}" != "{}"'.format(
                self.slink, search_text, expected_text))


class MobileBgAd(VehicleTypeMixin, models.Model):
    topmenu = models.IntegerField()
    adv = models.BigIntegerField(unique=True)

    # Computed fields
    active = models.BooleanField(default=True, db_index=True)
    first_update = models.ForeignKey('mobile_bg.MobileBgAdUpdate', models.CASCADE,
                                     null=True, related_name='first_update_ads')
    last_update = models.ForeignKey('mobile_bg.MobileBgAdUpdate', models.CASCADE,
                                    null=True, related_name='last_update_ads')
    last_active_update = models.ForeignKey('mobile_bg.MobileBgAdUpdate', models.CASCADE,
                                           null=True, related_name='last_active_update_ads')
    last_price_change = models.ForeignKey('mobile_bg.MobileBgAdUpdate', models.CASCADE,
                                          null=True, related_name='last_price_change_ads')
    last_full_update = models.ForeignKey('mobile_bg.MobileBgAdUpdate', models.CASCADE,
                                         null=True, related_name='last_full_update_ads')

    @property
    def url(self):
        return 'https://www.mobile.bg/pcgi/mobile.cgi?{}'.format(
            urlencode({
                'topmenu': self.topmenu,
                'act': '4',
                'adv': self.adv,
            }))

    def update_computed_fields(self):
        updates = list(self.updates.order_by('date'))
        if not len(updates):
            return
        self.first_update = updates[0]
        self.last_update = updates[-1]
        self.active = self.last_update.active

        self.last_price_change = None
        for update, prev in zip(updates[::-1], updates[-2::-1]):
            valid = (
                    update.active and
                    (update.price != prev.price or update.price_currency != prev.price_currency)
            )
            if valid:
                self.last_price_change = update
                break

        self.last_active_update = None
        for update in updates[::-1]:
            if update.active:
                self.last_active_update = update
                break
        for update in updates[::-1]:
            if update.type == MobileBgAdUpdate.TYPE_FULL:
                self.last_full_update = update
                break

    def update(self):
        resp = requests_get_retry(self.url)
        sleep(settings.REQUEST_DELAY)
        text = resp.content.decode('windows-1251')
        up = MobileBgAdUpdate.from_html(self, text)

        self.update_computed_fields()
        self.save()

        if up.active:
            self.download_images()

    def update_partial(self, el):
        raw_price = el.parent.next_sibling.next_sibling.text
        if raw_price.strip() == 'Договаряне':
            price, price_currency = MobileBgAdUpdate.PRICE_BY_NEGOTIATION, None
        else:
            price, price_currency = parse_mobile_bg_price(raw_price)
        MobileBgAdUpdate.from_price_partial(self, price, price_currency)

        self.update_computed_fields()
        self.save()

    def get_filtered_updates(self):
        updates = list(self.updates.order_by('date').all())
        filtered = []
        if len(updates) > 0:
            filtered = []
            for update in updates:
                if not update.active:
                    continue
                if len(filtered) < 1 or update.price != filtered[-1].price:
                    filtered.append(update)

            if updates[-1].date_tz.date() != filtered[-1].date_tz.date():
                filtered.append(updates[-1])
        return filtered

    @transaction.atomic()
    def download_images(self):
        if not self.last_active_update:
            print('No active update for ad', self.adv)
            return
        urls_match = re.search('\s* var picts=new Array\((.*)\);\n', self.last_active_update.html)
        if not urls_match:
            print('No images for ad', self.adv)
            return
        urls = urls_match.group(1)
        urls = urls.replace('"', '\\"').replace("'", '"')
        urls_list = ['https:' + i for i in json.loads('[{}]'.format(urls))]
        urls_list.sort()
        images = []
        for big_url in urls_list:
            index = int(re.search(r'_(\d+)\.pic$', big_url).group(1))

            try:
                self.images.get(index=index)
                print('Image {} already downloaded'.format(big_url))
                continue
            except MobileBgAdImage.DoesNotExist:
                pass

            small_url = big_url.replace('/big/', '/small/')
            ad_image = MobileBgAdImage(
                ad=self,
                index=index,
                small_url=small_url,
                big_url=big_url,
            )
            images.append(ad_image)
        pool = dummy.Pool(5)

        pool.map(lambda i: i.download(), images)
        pool.close()
        for image in images:
            image.save()

    @classmethod
    def from_url(cls, vehicle_type, url):
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        adv = qs['adv'][0]
        try:
            return cls.objects.get(adv=adv)
        except cls.DoesNotExist:
            return cls.objects.create(
                topmenu=qs['topmenu'][0],
                adv=adv,
                vehicle_type=vehicle_type,
            )

    @classmethod
    def get_recent_price_changes(cls):
        return MobileBgAd.objects.filter(
            active=True,
            last_price_change__isnull=False,
        ).order_by('-last_price_change__date')

    @classmethod
    def get_recent_unlists(cls):
        return MobileBgAd.objects.filter(
            active=False,
            last_active_update__isnull=False,
        ).order_by('-last_active_update__date')


def _image_big_upload_to(i, f):
    return 'mobile_bg/ads/{}/{}/{}'.format(str(i.ad.adv)[-3:], i.ad.adv, f)


class MobileBgAdImage(models.Model):
    ad = models.ForeignKey(MobileBgAd, models.CASCADE, related_name='images')
    index = models.IntegerField()
    small_url = models.CharField(max_length=512)
    big_url = models.CharField(max_length=512)
    image_big = models.FileField(upload_to=_image_big_upload_to)

    def _download(self, url):
        try:
            print('Downloading image {}'.format(url))
            resp = requests_get_retry(url)
            sleep(settings.REQUEST_DELAY / 2)
            return ContentFile(resp.content, '{}.jpg'.format(self.index))
        except HttpNotFoundException:
            return None

    def download(self):
        self.image_big = self._download(self.big_url)

    class Meta:
        unique_together = (('ad', 'index'),)


class MobileBgAdUpdate(ColorMixin, models.Model):
    TYPE_FULL = 0
    TYPE_PRICE_ONLY = 1
    TYPE_CHOICES = (
        (TYPE_FULL, 'Full'),
        (TYPE_PRICE_ONLY, 'Price Only'),
    )

    CURRENCY_BGN = 0
    CURRENCY_EUR = 1
    CURRENCY_USD = 2
    CURRENCY_CHOICES = (
        (CURRENCY_BGN, 'BGN'),
        (CURRENCY_EUR, 'EUR'),
        (CURRENCY_USD, 'USD'),
    )

    ENGINE_PETROL = 0
    ENGINE_DIESEL = 1
    ENGINE_HYBRID = 2
    ENGINE_ELECTRIC = 3
    ENGINE_CHOICES = (
        (ENGINE_PETROL, 'Petrol'),
        (ENGINE_DIESEL, 'Diesel'),
        (ENGINE_HYBRID, 'Hybrid'),
        (ENGINE_ELECTRIC, 'Electric'),
    )

    TRANSMISSION_MANUAL = 0
    TRANSMISSION_AUTOMATIC = 1
    TRANSMISSION_SEMIAUTOMATIC = 2
    TRANSMISSION_CHOICES = (
        (TRANSMISSION_MANUAL, 'Manual'),
        (TRANSMISSION_AUTOMATIC, 'Automatic'),
        (TRANSMISSION_SEMIAUTOMATIC, 'Semiautomatic'),
    )

    PRICE_BY_NEGOTIATION = -1

    date = models.DateTimeField(default=timezone.now, db_index=True)
    ad = models.ForeignKey(MobileBgAd, models.CASCADE, related_name='updates')
    type = models.IntegerField(default=TYPE_FULL, choices=TYPE_CHOICES)
    prev_update = models.OneToOneField('self', models.CASCADE,
                                       null=True, related_name='next_update')
    active = models.BooleanField(default=True, db_index=True)

    html_raw = models.TextField(null=True, blank=True)
    html_delta = models.BinaryField(null=True, blank=True)
    html_checksum = models.CharField(max_length=32)

    model_name = models.CharField(max_length=128)
    model_mod = models.CharField(max_length=128)
    price = models.IntegerField(null=True, blank=True)
    price_currency = models.IntegerField(null=True, blank=True, choices=CURRENCY_CHOICES)
    registration_date = models.DateField(null=True, blank=True)
    engine_type = models.IntegerField(null=True, blank=True, choices=ENGINE_CHOICES)
    mileage_km = models.IntegerField(null=True, blank=True)
    power_hp = models.IntegerField(null=True, blank=True)
    transmission_type = models.IntegerField(null=True, blank=True, choices=TRANSMISSION_CHOICES)

    @property
    def date_tz(self):
        return self.date.astimezone(settings.TZ)

    @property
    def html(self):
        if self.html_delta:
            result = bsdiff4.patch(
                self.prev_update.html.encode(),
                self.html_delta,
            ).decode()
        elif self.html_raw:
            result = self.html_raw
        else:
            result = self.prev_update.html

        result_checksum = hashlib.md5((result or '').encode()).hexdigest()
        if result_checksum != self.html_checksum:
            raise Exception('Update {} HTML failed verification. Expected {}, got {}.'.format(
                self.id, self.html_checksum, result_checksum))

        return result

    @html.setter
    def html(self, value):
        self.html_raw = value
        self.html_checksum = hashlib.md5((self.html_raw or '').encode()).hexdigest()

    def try_compress(self):
        # Already no data, same HTML as previous
        if self.html_raw is None and self.html_delta is None:
            return

        # Check if HTML is the same and we can remove all the data
        if self.prev_update and self.html == self.prev_update.html:
            self.html_raw = None
            self.html_delta = None
            return

        # Already delta-compressed
        if self.html_delta:
            return

        # If there's a prev_update, we can delta-compress
        assert self.html_raw
        if self.prev_update:
            self.html_delta = bsdiff4.diff(
                self.prev_update.html.encode(),
                self.html_raw.encode(),
            )
            self.html_raw = None

    def update_from_html(self):
        if self.type == self.TYPE_PRICE_ONLY:
            prev = self.prev_update
            while not prev.active:
                prev = prev.prev_update
                if prev is None:
                    return

            self.model_name = prev.model_name
            self.model_mod = prev.model_mod
            self.registration_date = prev.registration_date
            self.engine_type = prev.engine_type
            self.mileage_km = prev.mileage_km
            self.power_hp = prev.power_hp
            return

        bs = BeautifulSoup(self.html, 'html5lib')
        if len(bs.find_all(style='font-size:18px; font-weight:bold; color:#FF0000')):
            self.active = False
            return
        self.active = True

        price_by_negotiation = bs.find(style='font-size:13px; font-weight:bold;')
        if price_by_negotiation:
            self.price, self.price_currency = self.PRICE_BY_NEGOTIATION, None
        else:
            raw_price = bs.find(style='font-size:15px; font-weight:bold;').text
            self.price, self.price_currency = parse_mobile_bg_price(raw_price)

        raw_name = bs.find(style='font-size:18px; font-weight:bold;')
        raw_name_children = list(raw_name.children)
        if len(raw_name_children) >= 1:
            self.model_name = str(raw_name_children[0]).strip()
        if len(raw_name_children) >= 2:
            self.model_mod = raw_name_children[1].text.strip()

        def _get_info_row(title):
            title_el = bs.find(text=title)
            if title_el is None:
                return None
            return title_el.parent.next_sibling.text

        reg_date_row = _get_info_row('Дата на производство')
        if reg_date_row:
            reg_date_parts = reg_date_row.split()
            month = ['януари', 'февруари', 'март', 'април', 'май', 'юни', 'юли', 'август',
                     'септември', 'октомври', 'ноември', 'декември'].index(reg_date_parts[0]) + 1
            year = int(reg_date_parts[1])
            assert len(reg_date_parts) == 3
            assert reg_date_parts[2] == 'г.'
            self.registration_date = date(year, month, 1)

        engine_type_row = _get_info_row('Тип двигател')
        if engine_type_row:
            self.engine_type = {
                'Бензинов': self.ENGINE_PETROL,
                'Дизелов': self.ENGINE_DIESEL,
                'Хибриден': self.ENGINE_HYBRID,
                'Електрически': self.ENGINE_ELECTRIC,
            }[engine_type_row]

        mileage_row = _get_info_row('Пробег')
        if mileage_row:
            mileage_parts = mileage_row.split()
            self.mileage_km = int(mileage_parts[0])
            assert mileage_parts[1] == 'км'

        power_row = _get_info_row('Мощност')
        if power_row:
            power_parts = power_row.split()
            self.power_hp = int(power_parts[0])
            assert power_parts[1] == 'к.с.'

        transmission_type_row = _get_info_row('Скоростна кутия')
        if transmission_type_row:
            self.transmission_type = {
                'Ръчна': self.TRANSMISSION_MANUAL,
                'Автоматична': self.TRANSMISSION_AUTOMATIC,
                'Полуавтоматична': self.TRANSMISSION_SEMIAUTOMATIC,
            }[transmission_type_row]

        color_row = _get_info_row('Цвят')
        if color_row:
            self.color = self.color_to_code(color_row)

    @classmethod
    def from_price_partial(cls, ad, price, price_currency):
        prev_update = ad.last_update
        update = cls(
            ad=ad,
            type=cls.TYPE_PRICE_ONLY,
            prev_update=prev_update,
            html=None,
            active=True,
            price=price,
            price_currency=price_currency,
        )
        update.update_from_html()
        update.try_compress()
        update.save()
        return update

    @classmethod
    def from_html(cls, ad, html):
        update = cls(
            ad=ad,
            type=cls.TYPE_FULL,
            prev_update=ad.last_update,
            html=html,
        )
        update.update_from_html()
        update.try_compress()
        update.save()
        return update

    def __str__(self):
        return 'Update {} at {} {} at {} {}'.format(
            self.id,
            self.date.strftime('%Y-%m-%d %H:%M'),
            'active' if self.active else 'inactive',
            self.price,
            self.get_price_currency_display(),
        )

    class Meta:
        ordering = ('date',)
