from django.contrib import admin

from .models import WebhookConfig

class WebhookConfigAdmin(admin.ModelAdmin):
    list_display = ('resource', 'hook', 'action', 'third_party', 'url')

admin.site.register(WebhookConfig, WebhookConfigAdmin)
