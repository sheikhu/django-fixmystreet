from django.contrib import admin

from django_fixmystreet.fmsproxy.models import FMSProxy

class FMSProxyAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {"slug": ("name",)}

admin.site.register(FMSProxy, FMSProxyAdmin)
