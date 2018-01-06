from django.contrib import admin
from django.contrib.humanize.templatetags import humanize

from mobile_bg.models import MobileBgAd, MobileBgScrapeLink, MobileBgAdUpdate


class MobileBgScrapeLinkAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'vehicle_type',
        'min_price',
        'max_price',
        'slink',
        'ad_count',
        'last_updated'
    )
    list_per_page = 200
    list_filter = ('vehicle_type',)

    def last_updated(self, obj):
        return humanize.naturaltime(obj.last_update_date)

    last_updated.admin_order_field = 'last_update_date'


class MobileBgAdUpdateInline(admin.TabularInline):
    model = MobileBgAdUpdate
    fields = ('date', 'active', 'price', 'price_currency')
    extra = 0


class MobileBgAdAdmin(admin.ModelAdmin):
    list_display = (
        'adv',
        'active',
        'get_model',
    )
    readonly_fields = (
        'first_update',
        'last_update',
        'last_active_update',
        'last_price_change',
    )
    inlines = (MobileBgAdUpdateInline,)
    search_fields = ('adv',)

    def get_model(self, obj):
        return '{} {}'.format(
            obj.first_update.model_name,
            obj.first_update.model_mod,
        )

    get_model.short_description = 'Model name'


admin.site.register(MobileBgAd, MobileBgAdAdmin)
admin.site.register(MobileBgScrapeLink, MobileBgScrapeLinkAdmin)
