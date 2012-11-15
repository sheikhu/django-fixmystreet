from django import forms
from django_fixmystreet.fixmystreet.models import FMSUser, getLoggedInUserId
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from django.conf import settings
from django.utils.translation import ugettext_lazy
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required
import time


class ManagersChoiceField (forms.fields.ChoiceField):

	def __init__(self,  *args, **kwargs):
		choices = []
		#currentUserOrganisationId = 1
		if Session.objects.all()[0].session_key:
			currentUserOrganisation = FMSUser.objects.get(pk=getLoggedInUserId(Session.objects.all()[0].session_key)).organisation
		managers = FMSUser.objects.filter(manager=True).order_by('last_name', 'first_name')
		managers = managers.filter(organisation_id=currentUserOrganisation.id)

		for manager in managers:
			choices.append((manager.pk,manager.last_name+" "+manager.first_name))

		super(ManagersChoiceField,self).__init__(choices,*args,**kwargs)

	def refreshChoices(self):
		choices = []
		currentUserOrganisationId = 1
		if Session.objects.all()[0].session_key:
			currentUserOrganisation = FMSUser.objects.get(pk=getLoggedInUserId(Session.objects.all()[0].session_key)).organisation
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
	def __init__(self,  *args, **kwargs):
		super(ManagersListForm, self).__init__(*args, **kwargs)
		self.manager = ManagersChoiceField(label="")
		
	
	def refreshChoices(self):
		self.manager.refreshChoices()
	

class UserEditForm(UserChangeForm):
    class Meta:
        model = FMSUser
        fields = ('first_name','last_name',"username",'email','telephone','active',)
        
    telephone = forms.CharField(max_length="20",widget=forms.TextInput(attrs={ 'class': 'required' }),label=ugettext_lazy('Tel.'))
    active = forms.BooleanField(required=False)

    def save(self,userID, commit=True):
    	print "User id edited ="
        print userID
        fmsuser = FMSUser.objects.filter(user_ptr_id=userID)
        fmsuser.update(first_name = self.data["first_name"])
        fmsuser.update(last_name = self.data["last_name"])
        fmsuser.update(email = self.data["email"])
        fmsuser.update(telephone = self.data["telephone"])
        fmsuser.update(active=self.data['active'])
        return fmsuser;
