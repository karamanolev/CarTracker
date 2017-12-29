import json
import re
from datetime import date
from time import sleep
from urllib.parse import urlparse, parse_qs, urlencode

import bsdiff4
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models, transaction
from django.utils import timezone

from CarTracker.utils import requests_get_retry, HttpNotFoundException


class MobileBgScrapeLink(models.Model):
    slink = models.CharField(max_length=16)
    name = models.CharField(max_length=64)
    last_update_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('name',)


class MobileBgAd(models.Model):
    topmenu = models.IntegerField()
    act = models.IntegerField()
    adv = models.BigIntegerField(unique=True)

    # Computed fields
    active = models.BooleanField(default=True)
    first_update = models.ForeignKey('mobile_bg.MobileBgAdUpdate', models.CASCADE,
                                     null=True, related_name='first_update_ads')
    last_update = models.ForeignKey('mobile_bg.MobileBgAdUpdate', models.CASCADE,
                                    null=True, related_name='last_update_ads')
    last_active_update = models.ForeignKey('mobile_bg.MobileBgAdUpdate', models.CASCADE,
                                           null=True, related_name='last_active_update_ads')
    last_price_change = models.ForeignKey('mobile_bg.MobileBgAdUpdate', models.CASCADE,
                                          null=True, related_name='last_price_change_ads')

    @property
    def url(self):
        return 'https://www.mobile.bg/pcgi/mobile.cgi?{}'.format(
            urlencode({
                'topmenu': self.topmenu,
                'act': self.act,
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

    def update(self):
        resp = requests_get_retry(self.url)
        sleep(settings.REQUEST_DELAY)
        text = resp.content.decode('windows-1251')
        MobileBgAdUpdate.from_html(self, text)

        self.update_computed_fields()
        self.save()
        self.download_images()

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
            ad_image.download()
            ad_image.save()

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
                act=qs['act'][0],
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
        ).order_by('-last_active_update__date')


class MobileBgAdImage(models.Model):
    ad = models.ForeignKey(MobileBgAd, models.CASCADE, related_name='images')
    index = models.IntegerField()
    small_url = models.CharField(max_length=512)
    big_url = models.CharField(max_length=512)
    image_small = models.FileField(upload_to='mobile_bg/images/small/')
    image_big = models.FileField(upload_to='mobile_bg/images/big/')

    def _download(self, url):
        try:
            filename = '{}_{}.jpg'.format(self.ad.adv, self.index)
            print('Downloading image {}'.format(url))
            resp = requests_get_retry(url)
            sleep(settings.REQUEST_DELAY / 4)
            return ContentFile(resp.content, filename)
        except HttpNotFoundException:
            return None

    def download(self):
        self.image_small = self._download(self.small_url)
        self.image_big = self._download(self.big_url)

    class Meta:
        unique_together = (('ad', 'index'),)


class MobileBgAdUpdate(models.Model):
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

    date = models.DateTimeField(default=timezone.now)
    ad = models.ForeignKey(MobileBgAd, models.CASCADE, related_name='updates')
    prev_update = models.OneToOneField('self', models.CASCADE,
                                       null=True, related_name='next_update')

    html_raw = models.TextField(null=True)
    html_delta = models.BinaryField(null=True)

    model_name = models.CharField(max_length=128)
    model_mod = models.CharField(max_length=128)
    active = models.BooleanField(default=True, db_index=True)
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
        bs = BeautifulSoup(self.html, 'html.parser')
        if len(bs.find_all(style='font-size:18px; font-weight:bold; color:#FF0000')):
            self.active = False
            return
        self.active = True

        price_by_negotiation = bs.find(style='font-size:13px; font-weight:bold;')
        if price_by_negotiation:
            self.price = self.PRICE_BY_NEGOTIATION
        else:
            raw_price = bs.find(style='font-size:15px; font-weight:bold;').text.replace(' ', '')
            if 'лв.' in raw_price:
                self.price = int(raw_price.replace('лв.', ''))
                self.price_currency = self.CURRENCY_BGN
            elif 'EUR' in raw_price:
                self.price = int(raw_price.replace('EUR', ''))
                self.price_currency = self.CURRENCY_EUR
            elif 'USD' in raw_price:
                self.price = int(raw_price.replace('USD', ''))
                self.price_currency = self.CURRENCY_USD
            else:
                raise Exception('Unknown currency for price {}'.format(raw_price))

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
    def from_html(cls, ad, html):
        update = cls(
            ad=ad,
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
