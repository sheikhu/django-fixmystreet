
import logging

from django import forms
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import get_language
from django.utils.safestring import mark_safe

from apps.fixmystreet.models import (
    ReportMainCategoryClass, Report,
    ReportFile, ReportComment, ReportSubCategory,
    ReportCategory, ReportSecondaryCategoryClass, FMSUser, ReportReopenReason)
from apps.fixmystreet.utils import dict_to_point

# tricky stuff
from django.utils.functional import lazy
from django.utils import six
mark_safe_lazy = lazy(mark_safe, six.text_type)

logger = logging.getLogger("fixmystreet")

def secondaryCategoryChoices(show_private):
    choices = []
    choices.append(('', _("Select a secondary Category")))

    # HACK: Exclude Eclairage (id=6)
    category_classes = ReportSecondaryCategoryClass.objects.prefetch_related('categories').all().exclude(id=6).order_by('name_' + get_language())

    for category_class in category_classes:
        values = []

        categories = category_class.categories.all().order_by('name_' + get_language())

        if not show_private:
            categories = categories.filter(public=True)

        for category in categories:
            values.append((category.id, category.name))

        if len(categories):
            choices.append((category_class.name, values))

    # HACK: Add Eclairage (id=6) at the end
    category_class_eclairage = ReportSecondaryCategoryClass.objects.prefetch_related('categories').get(id=6)
    values = []

    categories = category_class_eclairage.categories.all().order_by('name_' + get_language())

    if not show_private:
        categories = categories.filter(public=True)

    for category in categories:
        values.append((category.id, category.name))

    if len(categories):
        choices.append((category_class_eclairage.name, values))

    return choices


class ReportForm(forms.ModelForm):
    """Report form"""
    required_css_class = 'required'

    class Meta:
        model = Report
        fields = "__all__"

    category = forms.ModelChoiceField(label=_("category"), empty_label=_("Select a Category"), queryset=ReportMainCategoryClass.objects.all().order_by('name_' + get_language()))
    secondary_category = forms.ModelChoiceField(label=_("Secondary category"), empty_label=_("Select a secondary Category"), queryset=ReportCategory.objects.filter(public=True).order_by('name_' + get_language()))
    sub_category = forms.ModelChoiceField(label=_("subcategory"), queryset=ReportSubCategory.objects.order_by('name_' + get_language()), widget=forms.RadioSelect, required=False)

    subscription = forms.BooleanField(label=_('Subscription and report follow-up'), initial=True, required=False)

    # hidden inputs
    address_nl = forms.CharField(widget=forms.widgets.HiddenInput)
    address_fr = forms.CharField(widget=forms.widgets.HiddenInput)
    address_number = forms.CharField(widget=forms.widgets.HiddenInput)
    postalcode = forms.CharField(widget=forms.widgets.HiddenInput)
    x = forms.CharField(widget=forms.widgets.HiddenInput)
    y = forms.CharField(widget=forms.widgets.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)
        #Ensure the good sortering when switching language.
        self.fields['category'].choices = forms.ModelChoiceField(label=_("category"), empty_label=_("Select a Category"), queryset=ReportMainCategoryClass.objects.all().order_by('name_' + get_language())).choices
        self.fields['secondary_category'].choices = secondaryCategoryChoices(False)

    def clean(self):
        cleaned_data = super(ReportForm, self).clean()

        # In the cas of a secondary_category with sub_categories is selected...
        if cleaned_data['secondary_category'].sub_categories.exists():
            # ... check that we receive the value of a sub_category
            if not cleaned_data['sub_category']:
                # If not, raise an error
                raise forms.ValidationError(self.error_messages['sub_category is required'])
        # If we receive a sub_category value but not corresponding of a secondary_category, raise an error
        elif cleaned_data['sub_category']:
            raise forms.ValidationError(self.error_messages['sub_category not expected'])

        return cleaned_data

    def save(self, commit=True):
        report = super(ReportForm, self).save(commit=False)

        report.point = dict_to_point(self.cleaned_data)
        report.status = Report.CREATED
        # report.address = self.cleaned_data["address"].split(", ")[0]
        # report.address_number = self.cleaned_data["address_number"]

        if commit:
            report.save()

        return report

    def saveForMobile(self, commit=True):
        report = super(ReportForm, self).save(commit=False)

        report.point = dict_to_point(self.cleaned_data)
        report.status = Report.TEMP
        # report.address = self.cleaned_data["address"].split(", ")[0]
        # report.address_number = self.cleaned_data["address_number"]

        if commit:
            report.save()

        return report


#Used by pro version
class ProReportForm(ReportForm):
    secondary_category = forms.ModelChoiceField(label=_("category"), empty_label=_("Select a secondary Category"), queryset=ReportCategory.objects.all().order_by('name_' + get_language()))
    private = forms.BooleanField(initial=True, required=False, label=_("Private Report"))

    def __init__(self, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)
        self.fields['secondary_category'].choices = secondaryCategoryChoices(True)

    class Meta:
        model = Report
        fields = ('x', 'y', 'address_nl', 'address_fr', 'address_number', 'postalcode', 'category', 'secondary_category', 'sub_category', 'postalcode', 'private', 'subscription')

    def save(self, commit=True):
        report = super(ProReportForm, self).save(commit=False)
        report.private = True  # self.cleaned_data['private']
        if commit:
            report.save()
        return report

    def saveForMobile(self, commit=True):
        report = super(ProReportForm, self).saveForMobile(commit=False)
        report.private = True  # self.cleaned_data['private']
        if commit:
            report.save()
        return report


#Used by citizen version only
class CitizenReportForm(ReportForm):
    """Citizen Report form"""

    terms_of_use_validated = forms.BooleanField(initial=False, required=True, label=mark_safe_lazy(_('I have read and accepted <a href="/terms-of-use/" target="_blank">the terms of use</a>')))

    class Meta:
        model = Report
        fields = (
            'x', 'y', 'address_nl', 'address_fr',
            'address_number', 'postalcode',
            'category', 'secondary_category', 'sub_category',
            'postalcode',
            'subscription',
            'terms_of_use_validated')

    def save(self, commit=True):
        report = super(CitizenReportForm, self).save(commit=False)
        # report.status = Report.CREATED # default value
        report.private = False
        #split address in 2 pieces

        if commit:
            report.save()

        return report

    def saveForMobile(self, commit=True):
        report = super(CitizenReportForm, self).saveForMobile(commit=False)
        # report.status = Report.CREATED # default value
        report.private = False
        #split address in 2 pieces

        if commit:
            report.save()

        return report

qualities = list(FMSUser.REPORT_QUALITY_CHOICES)


class CitizenForm(forms.Form):
    required_css_class = 'required'

    class Meta:
        model = FMSUser
        fields = ('last_name', 'telephone', 'email', 'quality')

    last_name = forms.CharField(max_length="30", label=_('Identity'), required=False)
    telephone = forms.CharField(max_length="20", label=_('Tel.'), required=False)
    email = forms.EmailField(max_length="75", label=_('Email'), widget=forms.TextInput(attrs={'class': 'validate-email'}))
    quality = forms.ChoiceField(label=_('Quality'), widget=forms.Select, choices=qualities)

    def clean(self):
        cleaned_data = super(CitizenForm, self).clean()
        for k in cleaned_data:
            if isinstance(cleaned_data[k], basestring):
                cleaned_data[k] = cleaned_data[k].strip()
        return cleaned_data

    def clean_email(self):
        # Force and ensure that email is case insensitive
        email = self.cleaned_data["email"].lower()

        try:
            user = FMSUser.objects.get(email__exact=email)

            if user.is_pro():
                raise ValidationError(_("You cannot use a pro email as citizen"))

        except FMSUser.DoesNotExist:
            pass
        except FMSUser.MultipleObjectsReturned:
            logger.error("Duplicate user : %s" % email)
            raise ValidationError(_("Duplicate user"))

        return email

    def save(self):
        try:
            instance = FMSUser.objects.get(email=self.cleaned_data["email"])
            if not bool(instance.is_pro()) and (
                instance.last_name.lower() != self.cleaned_data["last_name"].lower()
                or instance.telephone != self.cleaned_data["telephone"]
                or instance.quality != self.cleaned_data["quality"]
                or instance.last_used_language.upper() != get_language().upper()
            ):
                instance.last_name = self.cleaned_data["last_name"]
                instance.telephone = self.cleaned_data["telephone"]
                instance.quality = self.cleaned_data["quality"]
                instance.last_used_language = get_language()
                instance.clean()
                instance.save()
        except FMSUser.DoesNotExist:
            data = self.cleaned_data.copy()
            #For unique constraints
            data['username'] = data['email']
            data['is_active'] = False
            instance = FMSUser.objects.create(**data)

        return instance


class ReportFileForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = ReportFile
        fields = ('reportattachment_ptr', 'file', 'title', 'file_creation_date')

    file_creation_date = forms.CharField(widget=forms.HiddenInput(), required=False)
    title = forms.CharField(widget=forms.Textarea(attrs={'cols': 50, 'rows': 4,'placeholder': _('Your file description')}), required=False)

    def clean_file(self):
        f = self.cleaned_data['file']
        if f:
            if f.size > int(settings.MAX_UPLOAD_SIZE):
                raise ValidationError("File is too large")

            flength = len(f.name)
            if flength > 70:  # If filenameis longer than 70, truncate filename
                offset = flength - (flength % 40 + 20)  # modulus of file name + 20 to prevent file type truncation
                f.name = f.name[offset:]

        return f

    def clean_file_creation_date(self):
        file_creation_date = self.cleaned_data.get('file_creation_date')

        if not file_creation_date:
            # this is not None if user left the <input/> empty
            return None

        return file_creation_date

    def save(self, commit=True):
        report_file = super(ReportFileForm, self).save(commit=False)

        if commit:
            report_file.save()

        return report_file


class ReportCommentForm(forms.ModelForm):

    class Meta:
        model = ReportComment
        fields = ('text',)

    text = forms.fields.CharField(label="", widget=forms.Textarea(attrs={'placeholder': _("Add a comment, please.")}))


class ReportReopenReasonForm(ReportCommentForm):
    required_css_class = 'required'

    class Meta:
        model = ReportReopenReason
        fields = ('reason',)

    reason = forms.ChoiceField(choices=ReportReopenReason.REASON_CHOICES, widget=forms.RadioSelect())



class LoginForm(forms.Form):
    username = forms.CharField(label=_("Username"))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

    error_messages = {
        'invalid_login': _("Please enter a correct username and password. "
                           "Note that both fields are case-sensitive."),
        'no_cookies': _("Your Web browser doesn't appear to have cookies "
                        "enabled. Cookies are required for logging in."),
        'inactive': _("This account is inactive."),
    }

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user = authenticate(username=username,
                                     password=password)
            if self.user is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'])
            elif not self.user.is_active:
                raise forms.ValidationError(self.error_messages['inactive'])

        return self.cleaned_data

from django.contrib.auth.forms import PasswordResetForm
class FMSPasswordResetForm(PasswordResetForm):
    """
    Override PasswordResetForm to display an error message if the email is incorrect
    """
    error_messages = {
        'unknown': _("That email address doesn't have an associated "
                     "user account."),
        'unusable': _("The user account associated with this email "
                      "address cannot reset the password."),
    }

    def clean_email(self):
        """
        Validates that an active user exists with the given email address.
        """
        UserModel = get_user_model()
        email = self.cleaned_data["email"]
        users_cache = UserModel._default_manager.filter(email__iexact=email)
        if not len(users_cache):
            raise forms.ValidationError(self.error_messages['unknown'])
        if not any(user.is_active for user in users_cache):
            # none of the filtered users are active
            raise forms.ValidationError(self.error_messages['unknown'])
        if any((user.password == "!")
               for user in users_cache):
            raise forms.ValidationError(self.error_messages['unusable'])
        return email
