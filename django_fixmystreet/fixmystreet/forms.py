import datetime

from django import forms
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.utils.translation import get_language
from django.utils.safestring import mark_safe

from django_fixmystreet.fixmystreet.models import ReportMainCategoryClass, Report, ReportFile, ReportComment, \
                ReportCategory, ReportSecondaryCategoryClass, FMSUser
from django_fixmystreet.fixmystreet.utils import dict_to_point, get_current_user

# tricky stuff
from django.utils.functional import lazy
from django.utils import six
mark_safe_lazy = lazy(mark_safe, six.text_type)

def secondaryCategoryChoices(show_private):
    choices = []
    choices.append(('', _("Select a secondary Category")))
    category_classes = ReportSecondaryCategoryClass.objects.prefetch_related('categories').all().order_by('name_'+ get_language())

    for category_class in category_classes:
        values = []

        categories = category_class.categories.all().order_by('name_'+ get_language())
        if not show_private:
            categories = categories.filter(public=True)

        for category in categories:
            values.append((category.id, category.name))

        if len(categories):
            choices.append((category_class.name, values))

    return choices


class ReportForm(forms.ModelForm):
    """Report form"""
    required_css_class = 'required'

    class Meta:
        model = Report

    category = forms.ModelChoiceField(label=_("category"), empty_label=_("Select a Category"), queryset=ReportMainCategoryClass.objects.all().order_by('name_'+ get_language()))
    secondary_category = forms.ModelChoiceField(label=_("Secondary category"), empty_label=_("Select a secondary Category"), queryset=ReportCategory.objects.filter(public=True).order_by('name_'+ get_language()))
    subscription = forms.BooleanField(label=_('Subscription and report follow-up'), initial=True, required=False)

    # hidden inputs
    address_nl = forms.CharField(widget=forms.widgets.HiddenInput)
    address_fr = forms.CharField(widget=forms.widgets.HiddenInput)
    address_number = forms.CharField(widget=forms.widgets.HiddenInput)
    address_regional = forms.BooleanField(widget=forms.widgets.HiddenInput, required=False)
    postalcode = forms.CharField(widget=forms.widgets.HiddenInput)
    x = forms.CharField(widget=forms.widgets.HiddenInput)
    y = forms.CharField(widget=forms.widgets.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)
        #Ensure the good sortering when switching language.
        self.fields['category'].choices = forms.ModelChoiceField(label=_("category"), empty_label=_("Select a Category"), queryset=ReportMainCategoryClass.objects.all().order_by('name_'+ get_language())).choices
        self.fields['secondary_category'].choices = secondaryCategoryChoices(False)

    def save(self, commit=True):
        report = super(ReportForm, self).save(commit=False)

        report.point = dict_to_point(self.cleaned_data)
        report.status = Report.CREATED
        # report.address = self.cleaned_data["address"].split(", ")[0]
        # report.address_number = self.cleaned_data["address_number"]

        if commit:
            report.save()

        return report

#Used by pro version
class ProReportForm(ReportForm):
    secondary_category = forms.ModelChoiceField(label=_("category"), empty_label=_("Select a secondary Category"), queryset=ReportCategory.objects.all().order_by('name_'+ get_language()))
    private = forms.BooleanField(initial=True, required=False, label=_("Private Report"))

    def __init__(self, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)
        self.fields['secondary_category'].choices = secondaryCategoryChoices(True)

    class Meta:
        model = Report
        fields = ('x', 'y', 'address_nl','address_fr', 'address_number', 'address_regional', 'postalcode', 'category', 'secondary_category', 'postalcode','private', 'subscription')


    def save (self,commit=True):
        report= super(ProReportForm,self).save(commit=False)
        report.private = self.cleaned_data['private']
        if commit:
            report.save();
        return report


#Used by citizen version only
class CitizenReportForm(ReportForm):
    """Citizen Report form"""

    terms_of_use_validated = forms.BooleanField(initial=False, required=True, label=mark_safe_lazy(_('I have read and accepted <a href="/terms-of-use/" target="_blank">the terms of use</a>')))

    class Meta:
        model = Report
        fields = (
            'x', 'y', 'address_nl','address_fr',
            'address_number', 'address_regional', 'postalcode',
            'category', 'secondary_category',
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

qualities = list(FMSUser.REPORT_QUALITY_CHOICES)
qualities.insert(0, ('', _('Choose your quality')))

class CitizenForm(forms.Form):
    required_css_class = 'required'
    class Meta:
        model = FMSUser
        fields = ('last_name', 'telephone', 'email', 'quality')

    last_name = forms.CharField(max_length="30", label=_('Identity'), required=False)
    telephone = forms.CharField(max_length="20", label=_('Tel.'), required=False)
    email = forms.EmailField(max_length="75", label=_('Email'))
    quality = forms.ChoiceField(label=_('Quality'), choices=qualities)
    #citizen_firstname = forms.CharField(max_length="30", label=_('Firstname'))

    def save(self):
        try:
            instance = FMSUser.objects.get(email=self.cleaned_data["email"]);
        except FMSUser.DoesNotExist:
            data = self.cleaned_data.copy()
            #For unique constraints
            data['username'] = data['email']
            instance = FMSUser.objects.create(**data)
            instance.is_active = False

        return instance

    def validate_unique(self):
        """ disable unique validation, save will retrieve existing instance """
        pass

class ContactForm(forms.Form):
    required_css_class = 'required'

    name = forms.CharField(max_length=100,
                           widget=forms.TextInput(attrs={ 'class': 'required' }),
                           label=_('Name'))
    email = forms.EmailField(widget=forms.TextInput(attrs=dict({ 'class': 'required' },
                                                               maxlength=200)),
                             label=_('Email'))
    body = forms.CharField(widget=forms.Textarea(attrs={ 'class': 'required' }),
                              label=_('Message'))

    def save(self, fail_silently=False):
        message = render_to_string("emails/contact/message.txt", self.cleaned_data)
        send_mail('FixMyStreet User Message from %s' % self.cleaned_data['email'], message,
                   settings.DEFAULT_FROM_EMAIL,[settings.ADMIN_EMAIL], fail_silently=False)


class ReportFileForm(forms.ModelForm):
    required_css_class = 'required'
    class Meta:
        model = ReportFile
        fields = ('reportattachment_ptr', 'file', 'title', 'file_creation_date')

    file_creation_date = forms.CharField(widget=forms.HiddenInput(), required=False)
    title = forms.CharField ( widget=forms.widgets.Textarea(attrs={'rows':1, 'cols':40}), required=False)

    def clean_file(self):
        file = self.cleaned_data['file']
        if (file):
            if file._size > int(settings.MAX_UPLOAD_SIZE) and file._size == 0:
                raise ValidationError("File is too large")

        flength = len(file.name)
        if flength > 70: # If filenameis longer than 70, truncate filename
            offset = flength - (flength % 40 + 20) # modulus of file name + 20 to prevent file type truncation
            file.name = file.name[offset:]

        return file

    def clean_file_creation_date(self):
        file_creation_date = self.cleaned_data.get('file_creation_date')

        if not file_creation_date:
            # this is not None if user left the <input/> empty
            return None

        return file_creation_date

    def save(self, commit=True):
        report_file = super(ReportFileForm,self).save(commit=False)

        if (report_file.title == ''):
            report_file.title = report_file.file.name

        if commit:
            report_file.save()

        return report_file


class ReportCommentForm(forms.ModelForm):
    required_css_class = 'required'
    class Meta:
        model = ReportComment
        fields = ('text',)

    text = forms.fields.CharField(label="", required=False, widget=forms.Textarea(attrs={'placeholder':_("Add a comment, please.")}))


class MarkAsDoneForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ('mark_as_done_motivation',)

    def save(self, commit=True):
        report = super(MarkAsDoneForm,self).save(commit=False)
        report.status = Report.SOLVED
        report.mark_as_done_user = get_current_user()
        report.fixed_at = datetime.datetime.now()

        if commit:
            report.save()
        return report


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


