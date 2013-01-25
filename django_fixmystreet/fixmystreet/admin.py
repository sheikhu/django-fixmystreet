from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from django.core import urlresolvers

from django_fixmystreet.fixmystreet.models import ReportCategory, Report, FMSUser, ReportMainCategoryClass, ReportAttachment, FaqEntry, OrganisationEntity, ReportNotification, ReportEventLog


class FaqEntryAdmin(admin.ModelAdmin):
    list_display = ('q', 'order')

admin.site.register(FaqEntry, FaqEntryAdmin)


class ReportsInline(admin.TabularInline):
    model = Report
    fk_name = "responsible_manager"
    extra=0
    max_num=10

    fields = ("status", "address_nl","address_fr", "address_number", "postalcode", "secondary_category", "admin_url")
    readonly_fields = ("admin_url",)

    def admin_url(self, o):
        return "<a href='{0}'>admin</a>".format(urlresolvers.reverse('admin:fixmystreet_report_change', args=(o.id,)))
    admin_url.short_description = "edit URL"
    admin_url.allow_tags = True


class NotificationsInline(admin.TabularInline):
    model = ReportNotification
    fk_name = "recipient"
    fields = ("content_template", "success")
    extra=0
    max_num=10


class NotificationsInline(admin.TabularInline):
    model = ReportNotification
    fk_name = "recipient"
    fields = ("content_template", "success")
    extra=0
    max_num=10


class AttachmentsInline(admin.TabularInline):
    model = ReportAttachment
    fk_name = "report"
    fields = ("security_level", "created", "created_by")
    readonly_fields = ("created", "created_by",)
    extra=0
    max_num=10


class FMSUserAdmin(SimpleHistoryAdmin):
    list_display = ("get_full_name", "leader", "manager", "agent", "applicant", "contractor")
    inlines = (
        ReportsInline,
        # NotificationsInline,
        # UserEventsInline
    )
    # search_fields = ("username", "email", "first_name", "last_name")
    # list_filter = ("leader", "manager", "agent", "impetrant", "contractor")

admin.site.register(FMSUser,FMSUserAdmin)


class OrganisationEntityAdmin(SimpleHistoryAdmin):
    list_display = ("name", "commune", "region", "applicant", "subcontractor")
    search_fields = ("name",)
    list_filter = ("commune", "region", "applicant", "subcontractor")

admin.site.register(OrganisationEntity,OrganisationEntityAdmin)


class ReportEventsInline(admin.TabularInline):
    model = ReportEventLog
    fk_name = "report"
    fields = ("event_type", "event_at", "status_old", "status_new")
    readonly_fields = ("event_at",)
    extra=0
    max_num=10



class ReportAdmin(SimpleHistoryAdmin):
    list_display = ('responsible_entity', 'created', 'modified', 'category', 'secondary_category')
    ordering = ['modified']
    #exclude = ['photo']
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by')
    inlines = (
        AttachmentsInline,
        ReportEventsInline,
    )

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



