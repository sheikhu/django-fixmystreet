from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from django_fixmystreet.fixmystreet.models import ReportCategory, Report, FMSUser, ReportMainCategoryClass, FaqEntry, OrganisationEntity, ReportNotification


class FaqEntryAdmin(admin.ModelAdmin):
    list_display = ('q', 'order')

admin.site.register(FaqEntry, FaqEntryAdmin)


class FMSUserAdmin(admin.ModelAdmin):
    pass

admin.site.register(FMSUser,FMSUserAdmin)


class OrganisationEntityAdmin(SimpleHistoryAdmin):
    list_display = ('name',)

admin.site.register(OrganisationEntity,OrganisationEntityAdmin)


class ReportAdmin(SimpleHistoryAdmin):
    list_display = ('responsible_entity', 'created', 'modified', 'category', 'secondary_category')
    ordering = ['modified']
    #exclude = ['photo']

admin.site.register(Report,ReportAdmin)


class ReportNotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'sent_at', 'success')

admin.site.register(ReportNotification, ReportNotificationAdmin)


class ReportCategoryClassAdmin(admin.ModelAdmin):
    list_display = ('name',)
    
admin.site.register(ReportMainCategoryClass,ReportCategoryClassAdmin)


class ReportCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(ReportCategory, ReportCategoryAdmin)



