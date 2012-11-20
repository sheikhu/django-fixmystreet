from django import forms
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy
from django.contrib.gis.geos import fromstr
from django.forms.util import ErrorDict
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from django.utils.encoding import force_unicode
from django.utils.html import escape, conditional_escape

from django_fixmystreet.fixmystreet.models import ReportMainCategoryClass, ReportSecondaryCategoryClass, Commune, File, OrganisationEntity, Comment, Report, Status, ReportUpdate, ReportSubscription, ReportCategory, dictToPoint, AttachmentType, FMSUser

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
       
        super(SecondaryCategoryChoiceField,self).__init__(choices=choices,widget=SecondaryCategorySelect(attrs={'class':category.pk}),*args,**kwargs)



    def clean(self, value):
        super(SecondaryCategoryChoiceField,self).clean(value)
        try:
            #import pdb
            #pdb.set_trace()
            model = ReportCategory.objects.get(pk=value)
        except ReportCategory.DoesNotExist:
            raise ValidationError(self.error_messages['invalid_choice'])
        return model

#Used by PRO version
class ReportForm(forms.ModelForm):
    """Report form"""
    class Meta:
        model = Report
        fields = ('x', 'y', 'address', 'category', 'secondary_category', 'secondary_category_copy', 'photo', 'postalcode', 'description')

    required_css_class = 'required'
    secondary_category = SecondaryCategoryChoiceField(label=ugettext_lazy("Category"))
    secondary_category_copy = SecondaryCategoryChoiceField(label=ugettext_lazy("Category"),required=False)
    x = forms.fields.CharField(widget=forms.widgets.HiddenInput)
    y = forms.fields.CharField(widget=forms.widgets.HiddenInput)
    postalcode = forms.fields.CharField(widget=forms.widgets.HiddenInput,initial='1000')# Todo no initial value !
    photo = forms.fields.ImageField(required=False,widget=forms.widgets.FileInput(attrs={"accept":"image/*;capture=camera", "capture":"camera"}))

    def __init__(self,data=None, files=None, initial=None):
        if data:
            self.commune = Commune.objects.get(zipcode__code=data['postalcode'])
            self.point = dictToPoint(data)

        super(ReportForm,self).__init__(data, files, initial=initial)
        #self.fields['category'] = CategoryChoiceField(label=ugettext_lazy("Category"))

    def clean(self):
        if not self.commune:
            raise forms.ValidationError("Location not supported")
        return super(ReportForm, self).clean()

    def save(self, user, commit=True):
        report = super(ReportForm, self).save(commit=False)
        report.commune = self.commune
        report.status = Report.CREATED
        report.point = self.point
        report.private = True
        
        if user.is_authenticated():
            report.creator = user
	    #Detect who is the responsible Manager for the given type
	    #userCandidates = FMSUsers.objects.filter(organisation__id=user.organisation.id).filter(manager=True, categories__any=report.secondary_category)
            #loop elements to find the right user to assign
            #for (user in userCandidates):
            #     for (categoriesOfResponsability in user.categories)
            #          if (categoriesOfResponsability == report.secondary_category):
            #               report.responsible_manager = user 
        
        if commit:
            report.save()
        return report

#Used by citizen version only
class CitizenReportForm(ReportForm):
    """Citizen Report form"""
    class Meta:
        model = Report
        fields = ('x', 'y', 'address', 'category', 'secondary_category', 'quality', 'postalcode', 'photo', 'description', 'citizen_email', 'citizen_firstname','citizen_lastname')

    citizen_email = forms.CharField(max_length="50",widget=forms.TextInput(attrs={'class':'required'}),label=ugettext_lazy('Email'))
    citizen_firstname = forms.CharField(max_length="50",widget=forms.TextInput(),label=ugettext_lazy('Firstname'))
    citizen_lastname = forms.CharField(max_length="50",widget=forms.TextInput(),label=ugettext_lazy('Name'))

    def save(self, user, commit=True):
        #import pdb
        #pdb.set_trace()
        report = super(ReportForm, self).save(commit=False)
        report.commune = self.commune
        report.status = Report.CREATED 
        report.point = self.point
        report.private = False

        if user.is_authenticated():
            report.creator = user
        else:
            #Add information about the citizen connected.
            
            report.citizen = FMSUser.objects.create(username=self.cleaned_data["citizen_email"], email=self.cleaned_data["citizen_email"], first_name=self.cleaned_data["citizen_firstname"], last_name=self.cleaned_data["citizen_lastname"])
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
        if user.is_authenticated():
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
        fields = ('first_name','last_name','email','telephone','username','password1','password2','is_active')
    telephone = forms.CharField(max_length="20",widget=forms.TextInput(attrs={ 'class': 'required' }),label=ugettext_lazy('Tel.'))
    is_active = forms.BooleanField(required=False)
    def save(self,userID,isAgent,isManager,isContractor, commit=True):
        user = super(AgentCreationForm,self).save(commit=False)
        fmsuser = FMSUser(user_ptr=user)
        fmsuser.username = self.cleaned_data["username"]
        fmsuser.set_password(self.cleaned_data["password1"])
        fmsuser.first_name=self.cleaned_data["first_name"]
        fmsuser.last_name=self.cleaned_data["last_name"]
        fmsuser.email=self.cleaned_data["email"]
        fmsuser.telephone= self.cleaned_data['telephone']
        fmsuser.lastUsedLanguage="EN"
        
        if (self.data.__contains__('is_active')):
               isActive = True
        else:
               isActive = False
        fmsuser.is_active = isActive

        fmsuser.agent = (isAgent=="1")
        fmsuser.manager = (isManager=="1")
        #fmsuser.leader = (isImpetrant=="2")
	#In V1 all leaders are created in DB on application launch (in other words by sql queries)
        fmsuser.leader = False
        fmsuser.impetrant = False
        fmsuser.contractor = (isContractor=="1")
        currentUser = FMSUser.objects.get(user_ptr_id=userID)
        fmsuser.organisation = currentUser.organisation
        fmsuser.save()
        return fmsuser;
		
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
		#import pdb
                #pdb.set_trace()
		#default
		fileUpdate.fileType = AttachmentType.objects.all()[0];
		if (str(fileUpdate.file.name).endswith("pdf")):
			fileUpdate.fileType = AttachmentType.objects.get(pk=2);
		if (str(fileUpdate.file.name).endswith("doc")):
			fileUpdate.fileType = AttachmentType.objects.get(pk=3);
		if (str(fileUpdate.file.name).endswith("png")):
			fileUpdate.fileType = AttachmentType.objects.get(pk=4);
		if (str(fileUpdate.file.name).endswith("jpg")):
			fileUpdate.fileType = AttachmentType.objects.get(pk=1);
		
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
