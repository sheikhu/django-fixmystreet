

from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from django.core import urlresolvers
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.translation import ugettext_lazy as _
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.template.response import TemplateResponse
from django.conf.urls.defaults import patterns
from markdown import markdown

from django_fixmystreet.fixmystreet.models import ReportCategory, Report, FMSUser, ReportMainCategoryClass, ReportAttachment, FaqEntry, OrganisationEntity, ReportNotification, ReportEventLog, MailNotificationTemplate
from django_fixmystreet.fixmystreet.utils import export_as_csv_action

#admin.site.unregister(User)
#admin.site.unregister(Group)


class FaqEntryAdmin(admin.ModelAdmin):
    list_display = ('q', 'order')

admin.site.register(FaqEntry, FaqEntryAdmin)


class ReportsInline(admin.TabularInline):
    model = Report
    fk_name = "responsible_manager"
    extra=0
    max_num=10

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
    extra=0
    max_num=10


class UserEventsInline(admin.TabularInline):
    model = ReportEventLog
    fk_name = "user"
    fields = ("event_type", "event_at", "status_old", "status_new")
    readonly_fields = ("event_type", "event_at", "status_old", "status_new")
    extra=0
    max_num=10


class AttachmentsInline(admin.TabularInline):
    model = ReportAttachment
    fk_name = "report"
    fields = ("security_level", "created", "created_by")
    readonly_fields = ("security_level", "created", "created_by")
    extra=0
    max_num=10


class FMSUserAdmin(SimpleHistoryAdmin):
    list_display = ("get_full_name", "username", "organisation", "leader", "manager", "agent", "applicant", "contractor")
    inlines = (
        ReportsInline,
        NotificationsInline,
        UserEventsInline
    )
    readonly_fields = ("created", "created_by", "modified", "modified_by", "password", "username")
    search_fields = ("username", "email", "first_name", "last_name")
    list_filter = ("leader", "manager", "agent", "applicant", "contractor")

    actions = (
        export_as_csv_action(fields=list_display),
    )

    def get_urls(self):
        urls = super(FMSUserAdmin, self).get_urls()

        my_urls = patterns('',
            (r'^(\d+)/reset-password/$',
                     self.admin_site.admin_view(self.reset_password)
            ),
        )
        return my_urls + urls

    @sensitive_post_parameters()
    def reset_password(self, request, id, form_url=''):
        if not self.has_change_permission(request):
            raise PermissionDenied
        user = get_object_or_404(self.queryset(request), pk=id)
        if request.method == 'POST':
            form = AdminPasswordChangeForm(user, request.POST)
            if form.is_valid():
                form.save()
                msg = _('Password changed successfully.')
                messages.success(request, msg)
                return HttpResponseRedirect('..')
        else:
            form = AdminPasswordChangeForm(user)

        fieldsets = [(None, {'fields': form.base_fields.keys()})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            'title': _('Change password: %s') % escape(user.username),
            'adminForm': adminForm,
            'form_url': mark_safe(form_url),
            'form': form,
            'is_popup': '_popup' in request.REQUEST,
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': user,
            'save_as': False,
            'show_save': True,
        }
        return TemplateResponse(request, [
            'admin/auth/user/change_password.html'
        ], context, current_app=self.admin_site.name)

admin.site.register(FMSUser,FMSUserAdmin)


class OrgaUsersInline(admin.TabularInline):
    model = FMSUser
    fk_name = "organisation"
    fields = ("get_full_name", "username", "leader", "manager", "agent")
    readonly_fields = ("get_full_name", "username", "leader", "manager", "agent")
    extra=0
    max_num=10

class OrganisationEntityAdmin(SimpleHistoryAdmin):
    list_display = ("name", "commune", "region", "applicant", "subcontractor", "active")
    search_fields = ("name_fr", "name_nl",)
    list_filter = ("commune", "region", "applicant", "subcontractor")
    inlines = (
        OrgaUsersInline,
    )

admin.site.register(OrganisationEntity,OrganisationEntityAdmin)


class ReportEventsInline(admin.TabularInline):
    model = ReportEventLog
    fk_name = "report"
    fields = ("event_type", "event_at", "status_old", "status_new")
    readonly_fields = ("event_at",)
    extra=0
    max_num=10



class ReportAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'responsible_entity', 'status', 'created', 'modified', 'category', 'secondary_category')
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


class MailNotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'title')
    readonly_fields = ('content_html_fr', 'content_html_nl')
    def content_html_fr(self, o):
        return markdown(o.content_fr)

    def content_html_nl(self, o):
        return markdown(o.content_nl)
    content_html_fr.allow_tags = True
    content_html_nl.allow_tags = True


admin.site.register(MailNotificationTemplate, MailNotificationTemplateAdmin)

