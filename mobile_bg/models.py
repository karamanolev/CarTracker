from urllib.parse import urlparse, parse_qs, urlencode

from bs4 import BeautifulSoup
from django.conf import settings
from django.db import models
from django.utils import timezone

from CarTracker.utils import requests_get_retry


class MobileBgAd(models.Model):
    topmenu = models.IntegerField()
    act = models.IntegerField()
    adv = models.BigIntegerField(unique=True)
    active = models.BooleanField(default=True)
    first_update = models.ForeignKey('mobile_bg.MobileBgAdUpdate', models.CASCADE,
                                     null=True, related_name='first_update_ads')
    last_update = models.ForeignKey('mobile_bg.MobileBgAdUpdate', models.CASCADE,
                                    null=True, related_name='last_update_ads')

    @property
    def url(self):
        return 'https://www.mobile.bg/pcgi/mobile.cgi?{}'.format(
            urlencode({
                'topmenu': self.topmenu,
                'act': self.act,
                'adv': self.adv,
            }))

    def update(self):
        resp = requests_get_retry(self.url)
        text = resp.content.decode('windows-1251')
        update = MobileBgAdUpdate.from_html(self, text)
        if self.first_update is None:
            self.first_update = update
        self.active = update.active
        self.last_update = update
        self.save()

    def get_filtered_updates(self):
        updates = list(self.updates.order_by('date').all())
        filtered = []
        if len(updates) > 0:
            filtered = []
            for update in updates:
                if len(filtered) < 1 or update.price != filtered[-1].price:
                    filtered.append(update)

            if updates[-1].date_tz.date() != filtered[-1].date_tz.date():
                filtered.append(updates[-1])
        return filtered

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


class MobileBgAdUpdate(models.Model):
    PRICE_BY_NEGOTIATION = -1

    date = models.DateTimeField(default=timezone.now)
    ad = models.ForeignKey(MobileBgAd, models.CASCADE, related_name='updates')
    html = models.TextField()

    model_name = models.CharField(max_length=128)
    model_mod = models.CharField(max_length=128)
    active = models.BooleanField(default=True, db_index=True)
    price = models.IntegerField(null=True, blank=True)

    @property
    def date_tz(self):
        return self.date.astimezone(settings.TZ)

    def update_from_html(self, html):
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
            elif 'EUR' in raw_price:
                self.price = int(raw_price.replace('EUR', ''))
            else:
                raise Exception('Unknown currency for price {}'.format(raw_price))

        raw_name = bs.find(style='font-size:18px; font-weight:bold;')
        raw_name_children = list(raw_name.children)
        if len(raw_name_children) >= 1:
            self.model_name = str(raw_name_children[0]).strip()
        if len(raw_name_children) >= 2:
            self.model_mod = raw_name_children[1].text.strip()

    @classmethod
    def from_html(cls, ad, html):
        update = cls(
            ad=ad,
            html=html,
        )
        update.update_from_html(html)
        update.save()
        return update
