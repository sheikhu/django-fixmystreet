
from django import forms
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy, ugettext as _
from django.utils.encoding import force_unicode
from django.utils.html import escape, conditional_escape
from django.conf import settings

from django_fixmystreet.fixmystreet.models import ReportMainCategoryClass, Report, ReportFile, ReportComment, ReportCategory, ReportSecondaryCategoryClass, dictToPoint, FMSUser

class SecondaryCategorySelect(forms.Select):
    def render_option(self, selected_choices, option_value, option_label):
        option_value = force_unicode(option_value)
        if (option_value in selected_choices):
            selected_html = u' selected="selected"'
        else:
            selected_html = ''
        disabled_html = ''
        text_label = option_label;
        family_param = '';
        public_param = False;
        if isinstance(option_label, dict):
            if dict.get(option_label, 'disabled'):
                disabled_html = u' disabled="disabled"'
            if dict.get(option_label, 'label'):
                text_label = option_label['label']
            if dict.get(option_label, 'family'):
                family_param = option_label['family']
            if dict.get(option_label, 'public'):
                 if option_label['public'] == False:
                     public_param = False
                 else:
                     public_param = True
        return u'<option public="%s" family="%s"  value="%s"%s%s>%s</option>' % (
            escape(public_param), escape(family_param), escape(option_value), selected_html, disabled_html,
            conditional_escape(force_unicode(text_label)))



class SecondaryCategoryChoiceField(forms.fields.ChoiceField):
    """
    Do some pre-processing to
    render opt-groups (silently supported, but undocumented
    http://code.djangoproject.com/ticket/4412 )
    """
    def __init__(self,  *args, **kwargs):
        # assemble the opt groups.
        choices = []
        choices.append(('', ugettext_lazy("Select a Category")))
        categories = ReportCategory.objects.all()

        groups = {}
        for category in categories:
            catclass = str(category.secondary_category_class)
            if not groups.has_key(catclass):
                groups[catclass] = []
            groups[catclass].append((category.pk, {'label':category.name, 'family':category.category_class.pk, 'public':category.public}))

        for catclass, values in groups.items():
            choices.append((catclass,values))

        super(SecondaryCategoryChoiceField,self).__init__(choices=choices,widget=SecondaryCategorySelect(),*args,**kwargs)

    def clean(self, value):
        super(SecondaryCategoryChoiceField,self).clean(value)
        try:
            #import pdb
            #pdb.set_trace()
            model = ReportCategory.objects.get(pk=value)
        except ReportCategory.DoesNotExist:
            raise forms.ValidationError(self.error_messages['invalid_choice'])
        return model


class CategoryChoiceField(forms.fields.ChoiceField):
    """
    Do some pre-processing to
    render opt-groups (silently supported, but undocumented
    http://code.djangoproject.com/ticket/4412 )
    """
    def __init__(self,  *args, **kwargs):
        # assemble the opt groups.
        choices = []
        choices.append(('', ugettext_lazy("Select a Category")))
        categories = ReportMainCategoryClass.objects.all()

        uniqueCategory = ugettext_lazy("Main Category")
        groups = {}
        for category in categories:
            catclass = uniqueCategory
            if not groups.has_key(catclass):
                groups[catclass] = []
            if not groups[catclass].__contains__((category.pk, category.name)):
                groups[catclass].append((category.pk, category.name))

        for catclass, values in groups.items():
            choices.append((catclass,values))

        super(CategoryChoiceField,self).__init__(choices=choices,*args,**kwargs)

    def clean(self, value):
        super(CategoryChoiceField,self).clean(value)
        try:
            #import pdb
            #pdb.set_trace()
            model = ReportMainCategoryClass.objects.get(pk=value)
        except ReportCategory.DoesNotExist:
            raise forms.ValidationError(self.error_messages['invalid_choice'])
        return model


def secondaryCategoryChoices(show_private):
    choices = []
    choices.append(('', ugettext_lazy("Select a Category")))
    categories = ReportSecondaryCategoryClass.objects.prefetch_related('categories').all()

    for category_class in categories:
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
    secondary_category = forms.ModelChoiceField(label=ugettext_lazy("category"), empty_label=ugettext_lazy("Select a Category"), queryset=ReportCategory.objects.filter(public=True))

    # hidden inputs
    address = forms.CharField(widget=forms.widgets.HiddenInput)
    address_number = forms.CharField(widget=forms.widgets.HiddenInput)
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
        fields = ('x', 'y', 'address', 'address_number', 'postalcode', 'category', 'secondary_category', 'private')

    private = forms.BooleanField(initial=True)


qualities = list(Report.REPORT_QUALITY_CHOICES)
qualities.insert(0, ('', _('Choose your quality')))

#Used by citizen version only
class CitizenReportForm(ReportForm):
    """Citizen Report form"""

    class Meta:
        model = Report
        fields = ('x', 'y', 'address', 'address_number', 'postalcode', 'category', 'secondary_category', 'postalcode')

    def save(self, commit=True):
        report = super(CitizenReportForm, self).save(commit=False)
        # report.status = Report.CREATED # default value
        report.private = False
        #split address in 2 pieces
        # try:
        #     #Assign citizen
        #     report.citizen = FMSUser.objects.get(email=self.cleaned_data["citizen_email"])
        # except FMSUser.DoesNotExist:
        #     #Add information about the citizen connected if it does not exist
        #     report.citizen = FMSUser.objects.create(telephone=self.cleaned_data['telephone'],username=self.cleaned_data["citizen_email"], email=self.cleaned_data["citizen_email"], last_name=self.cleaned_data["citizen_lastname"], agent=False, contractor=False, manager=False, leader=False)

        if commit:
            report.save()

        return report

class CitizenForm(forms.ModelForm):
    required_css_class = 'required'
    class Meta:
        model = FMSUser
        fields = ('quality', 'email', 'lastname', 'subscription', 'telephone')

    quality = forms.ChoiceField(choices=qualities)
    email = forms.EmailField(max_length="75",label=ugettext_lazy('Email'))
    #citizen_firstname = forms.CharField(max_length="30", label=ugettext_lazy('Firstname'))
    lastname = forms.CharField(max_length="30", label=ugettext_lazy('Identity'), required=False)
    subscription = forms.BooleanField(required=False)
    telephone = forms.CharField(max_length="20",label=ugettext_lazy('Tel.'), required=False)


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
        model=ReportFile
        fields = ('file', 'text')

    title = forms.fields.CharField()
    text = forms.fields.CharField(widget=forms.Textarea)

    def clean_file(self):
        file = self.cleaned_data['file']
        if file._size > int(settings.MAX_UPLOAD_SIZE) and file._size == 0:
            raise forms.ValidationError("File is too large")
        #else:
         #   raise forms.ValidationError(_('File type is not supported'))
        return file

    def save(self, commit=True):
        fileUpdate= super(ReportFileForm, self).save(commit=False)

        loaded_file = self.files.get('file')

        if loaded_file.content_type == "application/pdf":
            fileUpdate.file_type = ReportFile.PDF
        elif loaded_file.content_type == 'application/msword' or loaded_file.content_type == 'application/vnd.oasis.opendocument.text' or loaded_file.content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            fileUpdate.file_type = ReportFile.WORD
        elif loaded_file.content_type == 'image/png' or loaded_file.content_type == 'image/jpeg':
            fileUpdate.file_type = ReportFile.IMAGE
        elif loaded_file.content_type == 'application/vnd.ms-excel' or loaded_file.content_type == 'application/vnd.oasis.opendocument.spreadsheet':
            fileUpdate.file_type = ReportFile.EXCEL
        fileUpdate.file_creation_date = self.data['file_creation_date']

        if commit:
            fileUpdate.save()
        return fileUpdate

class ReportCommentForm(forms.ModelForm):
    required_css_class = 'required'
    class Meta:
        model = ReportComment
        fields = ('text',)

    text = forms.fields.CharField(widget=forms.Textarea)

    def save(self,user,report,commit=True):
        comment= super(ReportCommentForm,self).save(commit=False)
        comment.report = report

        #Add the creator
        comment.creator = user

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
