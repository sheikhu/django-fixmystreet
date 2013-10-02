
import logging

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.template import TemplateDoesNotExist
from django.conf import settings

from django_fixmystreet.fixmystreet.models import FMSUser, Report

#Increase username size
AuthenticationForm.base_fields['username'].max_length = 150
AuthenticationForm.base_fields['username'].widget.attrs['maxlength'] = 150
AuthenticationForm.base_fields['username'].validators[0].limit_value = 150

logger = logging.getLogger(__name__)


class ManagersListForm(forms.Form):
    def __init__(self, user,  *args, **kwargs):
        self.manager = forms.ModelChoiceField(queryset=FMSUser.objects.filter(manager=True, organisation=user.organisation).order_by('last_name', 'first_name'))

        super(ManagersListForm, self).__init__(*args, **kwargs)


class RefuseForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ('refusal_motivation',)

    refusal_motivation = forms.CharField(
                required=True,
                label=_('Refusal motivation'),
                widget=forms.Textarea(attrs={
                    'placeholder': _("Refusal motivation description.")
                }))
    def save(self, commit=True):
        report = super(RefuseForm,self).save(commit=False)
        report.status = Report.REFUSED
        if commit:
            report.save()
        return report


class FmsUserForm(forms.ModelForm):
    required_css_class = 'required'
    class Meta:
        model = FMSUser
        fields = ('first_name','last_name','telephone','email','is_active')

    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True, label=_('Email'))
    telephone = forms.CharField(max_length="20")
    is_active = forms.BooleanField(required=False, initial=True, help_text="only active users can login.", label="Active")


class FmsUserCreateForm(FmsUserForm):

    def save(self, commit=True):
        user = self.retrive_user()
        self.password = False

        if not user:
            user = super(FmsUserCreateForm,self).save(commit=False)
            user.lastUsedLanguage = "FR"

        if user.logical_deleted:
            user.logical_deleted = False

        if not user.is_active:
            user.is_active = True

        if not user.password:
            self.password = User.objects.make_random_password()
            user.set_password(self.password)
            user.is_active = True

        if not user.username:
            user.username = self.cleaned_data["email"]

        if commit:
            user.save()
            self.notify_user()
        self.instance = user
        return user

    def validate_unique(self):
        """ disable unique validation, save will retrieve existing instance """
        pass

    def retrive_user(self):
        try:
            user = FMSUser.objects.get(email=self.cleaned_data['email'])
            self.instance_retrived = True
            return user
        except FMSUser.DoesNotExist:
            self.instance_retrived = False
            return None

    def notify_user(self):
        """
        Send directly an email to the created user
        (do not use the reportnotification class because then the password is saved in plain text in the DB)
        """

        if self.password:
            user = self.instance
            recipients = (user.email,)

            data = {
                "user": user,
                "password": self.password,
                "SITE_URL": 'http://{0}'.format(Site.objects.get_current().domain),
            }

            # MAIL SENDING...
            subject, html, text = '', '', ''
            try:
                subject = render_to_string('emails/send_created_to_user/subject.txt', data)
            except TemplateDoesNotExist:
                logger.error('template {0} does not exist'.format('emails/send_created_to_user/subject.txt'))
            try:
                text    = render_to_string('emails/send_created_to_user/message.txt', data)
            except TemplateDoesNotExist:
                logger.error('template {0} does not exist'.format('emails/send_created_to_user/message.txt'))

            try:
                html    = render_to_string('emails/send_created_to_user/message.html', data)
            except TemplateDoesNotExist:
                logger.info('template {0} does not exist'.format('emails/send_created_to_user/message.html'))

            subject = subject.rstrip(' \n\t').lstrip(' \n\t')

            msg = EmailMultiAlternatives(subject, text, settings.DEFAULT_FROM_EMAIL, recipients, headers={"Reply-To":user.created_by.email})
            if html:
                msg.attach_alternative(html, "text/html")

            msg.send()
            # MAIL SENDED


class SearchIncidentForm(forms.Form):
    status = forms.ChoiceField(choices=(
        ("", _("All Status")),
        ("created", _("Unpublished")),
        ("in_progress", _("In progress")),
        ("in_progress_and_assigned", _("In progress and assigned")),
        ("closed", _("Closed"))
    ), required=False)
    ownership = forms.ChoiceField(choices=(
        ("entity", _("All reports in my entity")),
        ("responsible", _("My responbsible reports")),
        ("subscribed", _("My subscriptions")),
        ("transfered", _("My transfered reports"))
    ), required=False)
