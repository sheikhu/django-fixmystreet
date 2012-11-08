from django import forms
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy
from django.contrib.gis.geos import fromstr
from django.forms.util import ErrorDict
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from django_fixmystreet.fixmystreet.models import Ward,File, Comment, Report, Status, ReportUpdate, ReportSubscription, ReportCategoryClass, ReportCategory, dictToPoint, Agent, AttachmentType


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
        categories = ReportCategory.objects.all()

        groups = {}
        for category in categories:
            catclass = str(category.category_class)
            if not groups.has_key(catclass):
                groups[catclass] = []
            groups[catclass].append((category.pk, category.name))
        for catclass, values in groups.items():
            choices.append((catclass,values))
        super(CategoryChoiceField,self).__init__(choices,*args,**kwargs)

    def clean(self, value):
        super(CategoryChoiceField,self).clean(value)
        try:
            model = ReportCategory.objects.get(pk=value)
        except ReportCategory.DoesNotExist:
            raise ValidationError(self.error_messages['invalid_choice'])
        return model
  

class ReportForm(forms.ModelForm):
    """Report form"""
    class Meta:
        model = Report
        fields = ('x','y','title', 'address', 'category','postalcode','description')

    required_css_class = 'required'
    category = CategoryChoiceField(label=ugettext_lazy("Category"))
    x = forms.fields.CharField(widget=forms.widgets.HiddenInput)
    y = forms.fields.CharField(widget=forms.widgets.HiddenInput)
    postalcode = forms.fields.CharField(widget=forms.widgets.HiddenInput,initial='1000')# Todo no initial value !
    # address = forms.fields.CharField(widget=forms.widgets.HiddenInput)
    
    
    def __init__(self,data=None, files=None, initial=None):
        if data:
            self.ward = Ward.objects.get(zipcode__code=data['postalcode'])
            self.point = dictToPoint(data)
        
        super(ReportForm,self).__init__(data, files, initial=initial)
        #self.fields['category'] = CategoryChoiceField(label=ugettext_lazy("Category"))

    def clean(self):
        if not self.ward:
            raise forms.ValidationError("Location not supported")
        return super(ReportForm, self).clean()

    def save(self, user, commit=True):
        report = super(ReportForm, self).save(commit=False)
        report.ward = self.ward
        report.status = list(Status.objects.all())[0]
        report.point = self.point
        report.creator = user
        if commit:
            report.save()
        return report


class ReportUpdateForm(forms.ModelForm):
    class Meta:
        model = ReportUpdate
        fields = ('desc','photo',)
    
    photo = forms.fields.ImageField(required=False,widget=forms.widgets.FileInput(attrs={"accept":"image/*;capture=camera", "capture":"camera"}))
    
    def __init__(self,data=None, files=None, initial=None):
        super(ReportUpdateForm,self).__init__(data, files, initial=initial)
        
	
    def save(self, user, report, commit=True):
        update = super(ReportUpdateForm, self).save(commit=False)
        update.author = user
        update.report = report
        if commit:
            update.save()
        return update



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

class AgentCreationForm(UserCreationForm):
	class Meta:
		model = User
		fields = ('telephone',)
	
	telephone = forms.CharField(max_length="20",
                           widget=forms.TextInput(attrs={ 'class': 'required' }),
                           label=ugettext_lazy('Tel.'))
    
	def save(self, commit=True):
		user = super(AgentCreationForm, self).save(commit=False)
		user.save()
		agent = Agent(user=user)
		agent.telephone = self.cleaned_data['telephone']
		agent.lastUsedLanguage = "NL"
		agent.hashCode=0
		agent.save();
		return user;
		
class ReportFileForm(forms.ModelForm):
	class Meta:
		model=File
		fields=('title','file','isVisible',)
	
	file = forms.fields.FileField(required=True,widget=forms.widgets.FileInput())
	
	def __init__(self,data=None, files=None, initial=None):
		super(ReportFileForm,self).__init__(data, files, initial=initial)
	
	def save(self,user,report,commit=True):
		fileUpdate= super(ReportFileForm,self).save(commit=False)
		fileUpdate.report = report
		fileUpdate.fileType = AttachmentType.objects.all()[0];
		if commit:
			fileUpdate.save()
		return fileUpdate

class ReportCommentForm(forms.ModelForm):
	class Meta:
		model=Comment
		fields=('title','text','isVisible',)
	
	def save(self,user,report,commit=True):
		comment= super(ReportCommentForm,self).save(commit=False)
		comment.report = report
		if commit:
			comment.save()
		return comment
