from django.contrib import admin
from django import forms
from transmeta import canonical_fieldname
from simple_history.admin import SimpleHistoryAdmin

from django_fixmystreet.fixmystreet.models import ReportCategory, Report, ReportMainCategoryClass, FaqEntry, OrganisationEntity


class ReportCategoryClassAdmin(admin.ModelAdmin):
    list_display = ('name',)
    
admin.site.register(ReportMainCategoryClass,ReportCategoryClassAdmin)


class ReportCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(ReportCategory, ReportCategoryAdmin)


class FaqEntryAdmin(admin.ModelAdmin):
    list_display = ('q', 'order')

# admin.site.register(FaqEntry, FaqEntryAdmin)


class ReportAdmin(SimpleHistoryAdmin):
    list_display = ('responsible_entity', 'created_at', 'updated_at', 'category', 'secondary_category')
    ordering = ['created_at']
    exclude = ['photo']

admin.site.register(Report,ReportAdmin)


class OrganisationEntityAdmin(SimpleHistoryAdmin):
    list_display = ('name',)

admin.site.register(OrganisationEntity, OrganisationEntityAdmin)




