from django.contrib import admin

from mobile_bg.models import MobileBgAd, MobileBgScrapeLink, MobileBgAdUpdate


class MobileBgScrapeLinkAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'min_price',
        'max_price',
        'slink',
        'ad_count',
    )
    list_per_page = 200


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
