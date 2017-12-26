from django.contrib import admin

from mobile_bg.models import MobileBgAd, MobileBgScrapeLink


class MobileBgScrapeLinkAdmin(admin.ModelAdmin):
    list_display = ('name', 'slink')


admin.site.register(MobileBgAd)
admin.site.register(MobileBgScrapeLink, MobileBgScrapeLinkAdmin)
