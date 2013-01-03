
from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.utils.translation import ugettext_lazy
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext as _


from django_fixmystreet.fixmystreet.models import FMSUser, Report


# TODO replace ALL this class by this single line: forms.ModelChoiceField(queryset=FMSUser.objects.filter(manager=True, organisation=connectedUser.organisation).order_by('last_name', 'first_name'), empty_label=None, widget=forms.RadioSelect)
class ManagersChoiceField(forms.fields.ChoiceField):

    def __init__(self, connectedUser, *args, **kwargs):
        choices = []
        managers = FMSUser.objects.filter(manager=True).order_by('last_name', 'first_name')
        managers = managers.filter(organisation=connectedUser.organisation)

        for manager in managers:
            choices.append((manager.pk,manager.last_name+" "+manager.first_name))

        super(ManagersChoiceField,self).__init__(choices,*args,**kwargs)

    def refreshChoices(self, connectedUser):
        choices = []
        currentUserOrganisation = FMSUser.objects.get(pk=connectedUser.id).organisation
        managers = FMSUser.objects.filter(manager=True).order_by('last_name', 'first_name')
        managers = managers.filter(organisation_id=currentUserOrganisation.id)

        for manager in managers:
            choices.append((manager.pk,manager.last_name+" "+manager.first_name))
        super(ManagersChoiceField, self)._set_choices(choices)

    def clean(self, value):
        super(ManagersChoiceField,self).clean(value)
        try:
            model = FMSUser.objects.get(pk=value)
        except FMSUser.DoesNotExist:
            raise ValidationError(self.error_messages['invalid_choice'])
        return model


class ManagersListForm(forms.Form):
    def __init__(self, connectedUser,  *args, **kwargs):
        super(ManagersListForm, self).__init__(*args, **kwargs)
        self.manager = ManagersChoiceField(connectedUser, label="")


    def refreshChoices(self, connectedUser):
        self.manager.refreshChoices(connectedUser)



class UserEditForm(UserChangeForm):
    class Meta:
        model = FMSUser
        fields = ('first_name','last_name',"username",'email','telephone','is_active')

    telephone = forms.CharField(max_length="20",widget=forms.TextInput(attrs={ 'class': 'required' }),label=ugettext_lazy('Tel.'))
    is_active = forms.BooleanField(required=True)

    def save(self,userID, commit=True):
        fmsuser = FMSUser.objects.filter(user_ptr_id=userID)
        fmsuser.update(first_name = self.data["first_name"])
        fmsuser.update(last_name = self.data["last_name"])
        fmsuser.update(email = self.data["email"])
        fmsuser.update(telephone = self.data["telephone"])
        if (self.data.__contains__('is_active')):
            isActive = True
        else:
            isActive = False
        fmsuser.update(is_active=isActive)
        return fmsuser;


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


class FmsUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('user_type','first_name','last_name','email','telephone','username','password1','password2','is_active')

    telephone = forms.CharField(max_length="20",widget=forms.TextInput(attrs={ 'class': 'required' }),label=ugettext_lazy('Tel.'))
    is_active = forms.BooleanField(required=False)
    user_type = forms.ChoiceField(label=ugettext_lazy("User type"),required=True, choices=(
        ("agent", _("Agent")),
        ("manager", _("Manager")),
        ("contractor", _("Contractor")),
    ))

    def save(self, userID, contractorOrganisation, user_type, commit=True):
        user = super(FmsUserForm,self).save(commit=False)
        fmsuser = FMSUser()
        user.fmsuser = fmsuser
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

        #In V1 all leaders are created in DB on application launch (in other words by sql queries)
        fmsuser.agent = (user_type == FMSUser.AGENT or user_type == FMSUser.MANAGER) #All gestionnaires are also agents
        fmsuser.manager = (user_type == FMSUser.MANAGER)
        fmsuser.contractor = (user_type == FMSUser.CONTRACTOR)
        currentUser = FMSUser.objects.get(user_ptr_id=userID)
        if (fmsuser.contractor):
             fmsuser.organisation = contractorOrganisation
        else:
             fmsuser.organisation = currentUser.organisation
        fmsuser.save()
        return fmsuser;
