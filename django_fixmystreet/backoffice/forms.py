
import logging

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.template import TemplateDoesNotExist
from django.conf import settings

from django_fixmystreet.fixmystreet.models import FMSUser, Report, OrganisationEntity

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
    required_css_class = 'required'
    class Meta:
        model = FMSUser
        fields = ('first_name','last_name','telephone','email','password1','password2','is_active')

    password1 = forms.CharField(widget=forms.PasswordInput(), label="Password" )
    password2 = forms.CharField(widget=forms.PasswordInput(), label="Repeat Password" )

    def clean(self,*args, **kwargs):
        self.clean_password()

    def clean_password(self):
        '''Snippet from Djanggo website: http://djangosnippets.org/snippets/191/'''
        if self.data['password1'] != self.data['password2']:
            raise forms.ValidationError('Passwords are not the same')
        return self.data['password1']

    def save(self, commit=True):
        user = self.retrive_user()
        if not user:
            user = super(FmsUserCreateForm,self).save(commit=False)
            user.lastUsedLanguage = "EN"

        if not user.password:
            user.set_password(self.cleaned_data["password1"])
            user.is_active = True

        if not user.username:
            user.username = self.cleaned_data["email"]

        self.promote(user)

        if commit:
            user.save()
            if not self.instance_retrived:
                self.notify_user(user)
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

    def promote(self, user):
        """ set flags for user role, must be extends """
        pass

    def notify_user(self, user):
        """
        Send directly an email to the created user
        (do not use the reportnotification class because then the password is saved in plain text in the DB)
        """
        recipients = (user.email,)

        data = {
            "user": user,
            "password":self.cleaned_data['password1'],
            "SITE_URL": Site.objects.get_current().domain
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

        msg = EmailMultiAlternatives(subject, text, settings.EMAIL_FROM_USER, recipients, headers={"Reply-To":user.created_by.email})
        if html:
            msg.attach_alternative(html, "text/html")

        msg.send()
        # MAIL SENDED


class AgentForm(FmsUserCreateForm):
    class Meta:
        model = FMSUser
        fields = ('user_type','first_name','last_name','telephone','email','password1','password2','is_active')

    user_type = forms.ChoiceField(label=_("User type"),required=True, choices=(
        ("agent", _("Agent")),
        ("manager", _("Manager")),
    ))


    def promote(self, user):
        user.agent = (self.cleaned_data['user_type'] == FMSUser.AGENT or self.cleaned_data['user_type'] == FMSUser.MANAGER) #All gestionnaires are also agents
        user.manager = (self.cleaned_data['user_type'] == FMSUser.MANAGER)


class ContractorUserForm(FmsUserCreateForm):

    def promote(self, user):
        user.contractor = True

class ContractorForm(forms.ModelForm):
    required_css_class = 'required'
    class Meta:
        model = OrganisationEntity
        fields = ('name_fr', 'name_nl', 'telephone')

    name_fr = forms.CharField()
    name_nl = forms.CharField()
    telephone = forms.CharField(required=False)

    def save(self, organisation, commit=True):
        contractor = super(ContractorForm, self).save(commit=False)
        contractor.subcontractor = True
        contractor.dependency = organisation

        if commit:
            contractor.save()
        return contractor

