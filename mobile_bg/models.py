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


class MobileBgScrapeLink(models.Model):
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
        bs = BeautifulSoup(text, 'html.parser')
        cell = bs.find(text='Резултат от Вашето търсене на:')
        search_text = cell.parent.parent.text
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
            '\nРезултат от Вашето търсене на:'
            '\n            Рубрика: Автомобили, {}; Състояние: Употребявани, Нови, '
            '{}'
            'Подредени по: Марка/Модел/Цена\n'
        ).format(
            self.name,
            expected_price,
        )
        if search_text != expected_text:
            raise Exception('Slink {} does not verify "{}" != "{}"'.format(
                self.slink, search_text, expected_text))


class MobileBgAd(models.Model):
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
        MobileBgAdUpdate.from_html(self, text)

        self.update_computed_fields()
        self.save()
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
    def from_url(cls, url):
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        adv = qs['adv'][0]
        try:
            return cls.objects.get(adv=adv)
        except cls.DoesNotExist:
            return cls.objects.create(
                topmenu=qs['topmenu'][0],
                adv=adv,
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


def _image_small_upload_to(i, f):
    return 'mobile_bg/ads/{}/{}/small/{}'.format(str(i.ad.adv)[-2:], i.ad.adv, f)


def _image_big_upload_to(i, f):
    return 'mobile_bg/ads/{}/{}/big/{}'.format(str(i.ad.adv)[-2:], i.ad.adv, f)


class MobileBgAdImage(models.Model):
    ad = models.ForeignKey(MobileBgAd, models.CASCADE, related_name='images')
    index = models.IntegerField()
    small_url = models.CharField(max_length=512)
    big_url = models.CharField(max_length=512)
    image_small = models.FileField(upload_to=_image_small_upload_to)
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
        self.image_small = self._download(self.small_url)
        self.image_big = self._download(self.big_url)

    class Meta:
        unique_together = (('ad', 'index'),)


class MobileBgAdUpdate(models.Model):
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

    PRICE_BY_NEGOTIATION = -1

    date = models.DateTimeField(default=timezone.now, db_index=True)
    ad = models.ForeignKey(MobileBgAd, models.CASCADE, related_name='updates')
    type = models.IntegerField(default=TYPE_FULL, choices=TYPE_CHOICES)
    prev_update = models.OneToOneField('self', models.CASCADE,
                                       null=True, related_name='next_update')
    active = models.BooleanField(default=True, db_index=True)

    html_raw = models.TextField(null=True)
    html_delta = models.BinaryField(null=True)

    model_name = models.CharField(max_length=128)
    model_mod = models.CharField(max_length=128)
    price = models.IntegerField(null=True, blank=True)
    price_currency = models.IntegerField(null=True, blank=True, choices=CURRENCY_CHOICES)
    registration_date = models.DateField(null=True, blank=True)
    engine_type = models.IntegerField(null=True, blank=True, choices=ENGINE_CHOICES)
    mileage_km = models.IntegerField(null=True, blank=True)
    power_hp = models.IntegerField(null=True, blank=True)

    @property
    def date_tz(self):
        return self.date.astimezone(settings.TZ)

    @property
    def html(self):
        if self.html_delta:
            return bsdiff4.patch(
                self.prev_update.html.encode(),
                self.html_delta,
            ).decode()
        else:
            return self.html_raw

    @html.setter
    def html(self, value):
        self.html_raw = value

    def try_compress(self):
        if self.html_raw and self.prev_update:
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

        bs = BeautifulSoup(self.html, 'html.parser')
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

    @classmethod
    def from_price_partial(cls, ad, price, price_currency):
        prev_update = ad.last_update
        update = cls(
            ad=ad,
            type=cls.TYPE_PRICE_ONLY,
            prev_update=prev_update,
            html=prev_update.html,
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
