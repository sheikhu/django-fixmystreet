
from django import forms
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy, ugettext as _
from django.core.validators import validate_email
from django.conf import settings

from django_fixmystreet.fixmystreet.models import ReportMainCategoryClass, Report, ReportFile, ReportComment, ReportCategory, ReportSecondaryCategoryClass, dictToPoint, FMSUser


def secondaryCategoryChoices(show_private):
    choices = []
    choices.append(('', ugettext_lazy("Select a Category")))
    category_classes = ReportSecondaryCategoryClass.objects.prefetch_related('categories').all()

    for category_class in category_classes:
        values = []

        categories = category_class.categories.all()
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

    category = forms.ModelChoiceField(label=ugettext_lazy("category"), empty_label=ugettext_lazy("Select a Category"), queryset=ReportMainCategoryClass.objects.all())
    secondary_category = forms.ModelChoiceField(label=ugettext_lazy("Secondary category"), empty_label=ugettext_lazy("Select a Category"), queryset=ReportCategory.objects.filter(public=True))

    # hidden inputs
    address = forms.CharField(widget=forms.widgets.HiddenInput)
    address_number = forms.CharField(widget=forms.widgets.HiddenInput)
    address_regional = forms.BooleanField(widget=forms.widgets.HiddenInput, required=False)
    postalcode = forms.CharField(widget=forms.widgets.HiddenInput)
    x = forms.CharField(widget=forms.widgets.HiddenInput)
    y = forms.CharField(widget=forms.widgets.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)
        self.fields['secondary_category'].choices = secondaryCategoryChoices(False)

    def save(self, commit=True):
        report = super(ReportForm, self).save(commit=False)

        report.point = dictToPoint(self.cleaned_data)
        report.status = Report.CREATED
        # report.address = self.cleaned_data["address"].split(", ")[0]
        # report.address_number = self.cleaned_data["address_number"]
        if commit:
            report.save()
        return report

#Used by pro version
class ProReportForm(ReportForm):
    secondary_category = forms.ModelChoiceField(label=ugettext_lazy("category"), empty_label=ugettext_lazy("Select a Category"), queryset=ReportCategory.objects.all())

    def __init__(self, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)
        self.fields['secondary_category'].choices = secondaryCategoryChoices(True)

    class Meta:
        model = Report
        fields = ('x', 'y', 'address', 'address_number', 'address_regional', 'postalcode', 'category', 'secondary_category', 'postalcode','private')

    private = forms.BooleanField(initial=True,required=False)

    def save (self,commit=True):
        report= super(ProReportForm,self).save(commit=False)
        report.private = self.cleaned_data['private']
        if commit:
            report.save();
        return report


#Used by citizen version only
class CitizenReportForm(ReportForm):
    """Citizen Report form"""

    quality = forms.ChoiceField(choices=FMSUser.REPORT_QUALITY_CHOICES)

    def __init__(self, *args, **kwargs):
        super(CitizenReportForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Report
        fields = ('x', 'y', 'address', 'address_number', 'address_regional', 'postalcode', 'category', 'secondary_category', 'postalcode', 'quality')

    def save(self, commit=True):
        report = super(CitizenReportForm, self).save(commit=False)
        # report.status = Report.CREATED # default value
        report.private = False
        #split address in 2 pieces

        if commit:
            report.save()

        return report

class CitizenForm(forms.Form):
    required_css_class = 'required'
    class Meta:
        model = FMSUser
        fields = ('last_name', 'telephone', 'email', 'quality', 'subscription')

    email = forms.EmailField(max_length="75",label=ugettext_lazy('Email'))
    #citizen_firstname = forms.CharField(max_length="30", label=ugettext_lazy('Firstname'))
    last_name = forms.CharField(max_length="30", label=ugettext_lazy('Identity'), required=False)
    subscription = forms.BooleanField(required=False)
    telephone = forms.CharField(max_length="20",label=ugettext_lazy('Tel.'), required=False)

    def save(self):
        try:
            instance = FMSUser.objects.get(email=self.cleaned_data["email"]);
        except FMSUser.DoesNotExist:
            del self.cleaned_data['subscription']
            #For unique constraints
            self.cleaned_data['username'] = self.cleaned_data['email']
            instance = FMSUser.objects.create(**self.cleaned_data)

        return instance

    def clean_email(self):
        email = self.cleaned_data['email']
        validate_email(email)
        return email


class ContactForm(forms.Form):
    required_css_class = 'required'

    name = forms.CharField(max_length=100,
                           widget=forms.TextInput(attrs={ 'class': 'required' }),
                           label=ugettext_lazy('Name'))
    email = forms.EmailField(widget=forms.TextInput(attrs=dict({ 'class': 'required' },
                                                               maxlength=200)),
                             label=ugettext_lazy('Email'))
    body = forms.CharField(widget=forms.Textarea(attrs={ 'class': 'required' }),
                              label=ugettext_lazy('Message'))

    def save(self, fail_silently=False):
        message = render_to_string("emails/contact/message.txt", self.cleaned_data )
        send_mail('FixMyStreet User Message from %s' % self.cleaned_data['email'], message,
                   settings.EMAIL_FROM_USER,[settings.ADMIN_EMAIL], fail_silently=False)


class ReportFileForm(forms.ModelForm):
    required_css_class = 'required'
    class Meta:
        model = ReportFile
        fields = ('reportattachment_ptr', 'file', 'title', 'file_creation_date')

    file_creation_date = forms.CharField(widget=forms.HiddenInput())

    # description = forms.fields.CharField(widget=forms.Textarea)

    def clean_file(self):
        file = self.cleaned_data['file']
        if file._size > int(settings.MAX_UPLOAD_SIZE) and file._size == 0:
            raise forms.ValidationError("File is too large")
        #else:
         #   raise forms.ValidationError(_('File type is not supported'))
        return file


class ReportCommentForm(forms.ModelForm):
    required_css_class = 'required'
    class Meta:
        model = ReportComment
        fields = ('text',)

    text = forms.fields.CharField(widget=forms.Textarea(attrs={'placeholder':_("Verify if a similar incident isn't reported yet.")}))

    def save(self, commit=True):
        comment= super(ReportCommentForm,self).save(commit=False)

        if commit:
            comment.save()
        return comment


class FileUploadForm(forms.Form):
    title = forms.CharField(max_length=50,required=False)
    file  = forms.FileField()

class MarkAsDoneForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ('mark_as_done_motivation',)

    def save(self, commit=True):
        report = super(MarkAsDoneForm,self).save(commit=False)
        report.status = Report.SOLVED
        if commit:
            report.save()
        return report
