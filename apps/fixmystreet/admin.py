from django.contrib import admin
from django.core import urlresolvers
from django.contrib.auth.models import User, Group

from simple_history.admin import SimpleHistoryAdmin

from .models import (
    ReportCategory, Report, FMSUser, ReportMainCategoryClass, ReportSecondaryCategoryClass,
    ReportAttachment, Page, FAQPage, OrganisationEntity, ReportNotification, ReportEventLog,
    UserOrganisationMembership
)
from .utils import export_as_csv_action

admin.site.unregister(User)
admin.site.unregister(Group)


class ReportsInline(admin.TabularInline):
    model = Report
    fk_name = "responsible_department"
    extra = 10

    fields = ("status", "address_fr", "address_number", "responsible_entity", "admin_url")
    readonly_fields = ("status", "address_fr", "address_number", "responsible_entity", "admin_url",)

    def admin_url(self, o):
        return "<a href='{0}'>admin</a>".format(urlresolvers.reverse('admin:fixmystreet_report_change', args=(o.id,)))
    admin_url.short_description = "edit URL"
    admin_url.allow_tags = True


class NotificationsInline(admin.TabularInline):
    model = ReportNotification
    fk_name = "recipient"
    fields = ("content_template", "success")
    readonly_fields = ("content_template", "success")
    extra = 0


class UserEventsInline(admin.TabularInline):
    model = ReportEventLog
    fk_name = "user"
    fields = ("event_type", "event_at", "status_old", "status_new")
    readonly_fields = ("event_type", "event_at", "status_old", "status_new")
    extra = 0


class AttachmentsInline(admin.TabularInline):
    model = ReportAttachment
    fk_name = "report"
    fields = ("security_level", "created", "created_by")
    readonly_fields = ("security_level", "created", "created_by")
    extra = 0


class UserMembershipsInline(admin.TabularInline):
    model = UserOrganisationMembership
    fk_name = "user"
    fields = ("contact_user", "organisation")
    extra = 0

class GroupMembershipsInline(admin.TabularInline):
    model = UserOrganisationMembership
    fk_name = "organisation"
    fields = ("contact_user", "organisation")
    extra = 0

class UserOrganisationMembershipAdmin(SimpleHistoryAdmin):
    list_display = ("organisation", "user")
    list_filter = ("organisation",)

admin.site.register(UserOrganisationMembership, UserOrganisationMembershipAdmin)

class FMSUserAdmin(SimpleHistoryAdmin):
    list_display = ("id", "get_full_name", "username", "organisation", "leader", "manager", "agent", "applicant", "contractor")
    list_display_links = list_display[:2]
    inlines = (
        UserMembershipsInline,
        # NotificationsInline,
        # UserEventsInline
    )
    readonly_fields = ("date_joined", "last_login", "created", "created_by", "modified", "modified_by", "password", "username")
    search_fields = ("username", "email", "first_name", "last_name")
    list_filter = ("leader", "manager", "agent", "applicant", "contractor")

    fieldsets = (
        (None, {
            'fields': (
                'created',
                'modified',
                'created_by',
                'modified_by',
                'last_login',
                'date_joined',
            )
        }),
        ('Informations', {
            'fields': (
                'first_name',
                'last_name',
                'telephone',
                'email',
                'last_used_language',
            )
        }),
        ('Django', {
            'fields': (
                'username',
                'password',
                'is_superuser',
                'is_staff',
                'is_active',
                'logical_deleted',
                'groups',
                'user_permissions',
            )
        }),
        ('Pro', {
            'description': 'Pro must be in an entity and are linked to groups by memberships',
            'fields': (
                'agent',
                'manager',
                'leader',
                'organisation',
            )
        }),
        ('Contractor', {
            'description': 'Contractors are linked to the contractor groups by memberships',
            'fields': (
                'applicant',
                'contractor',
            )
        })
    )

    actions = (
        export_as_csv_action(fields=list_display),
    )

admin.site.register(FMSUser, FMSUserAdmin)


class OrgaUsersInline(admin.TabularInline):
    model = FMSUser
    fk_name = "organisation"
    fields = ("get_full_name", "username", "leader", "manager", "agent", "is_active")
    readonly_fields = ("get_full_name", "username", "leader", "manager", "agent", "is_active")
    extra = 0

class GroupsInline(admin.TabularInline):
    model = OrganisationEntity
    fk_name = "dependency"
    fields = ('name_fr', 'type')
    extra = 0


class OrganisationEntityAdmin(SimpleHistoryAdmin):
    list_display = ("name", "type", "active")
    search_fields = ("name_fr", "name_nl",)
    list_filter = ("type",)
    inlines = (
        OrgaUsersInline,
        GroupMembershipsInline,
        GroupsInline,
    )

admin.site.register(OrganisationEntity, OrganisationEntityAdmin)


class ReportEventsInline(admin.TabularInline):
    model = ReportEventLog
    fk_name = "report"
    fields = ("event_type", "event_at", "status_old", "status_new")
    readonly_fields = ("event_at",)
    extra = 0


class ReportAdmin(SimpleHistoryAdmin):
    list_display = (
        'id', 'responsible_entity', 'responsible_department', 'status',
        'get_category_path'
    )
    search_fields = ('id',)
    list_filter = ('status',)
    ordering = ('-id', )
    exclude = (
        'photo',
    )
    readonly_fields = (
        'created', 'modified', 'created_by', 'modified_by', 'citizen',
        'merged_with'
    )
    inlines = (
        AttachmentsInline,
        ReportEventsInline,
    )

admin.site.register(Report, ReportAdmin)


class ReportNotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient_mail', 'sent_at', 'success')
    list_filter = ("success",)

admin.site.register(ReportNotification, ReportNotificationAdmin)


class ReportSecondaryCategoryClassAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(ReportSecondaryCategoryClass, ReportSecondaryCategoryClassAdmin)


class ReportMainCategoryClassAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(ReportMainCategoryClass, ReportMainCategoryClassAdmin)


class ReportCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_class', 'secondary_category_class')
    list_filter  = ('secondary_category_class',)

admin.site.register(ReportCategory, ReportCategoryAdmin)


class PageAdmin(SimpleHistoryAdmin):
    list_display = ('title', 'content')

admin.site.register(Page, PageAdmin)


class FAQPageAdmin(admin.ModelAdmin):
    list_display = ('id', 'title_fr', 'title_nl', 'visible', 'ranking')
    ordering = ('ranking', )

admin.site.register(FAQPage, FAQPageAdmin)
