from django import forms
from django_fixmystreet.fixmystreet.models import FMSUser, getLoggedInUserId
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import ugettext_lazy
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required


class ManagersChoiceField (forms.fields.ChoiceField):
	def __init__(self,  *args, **kwargs):
		choices = []
		choices.append(('', ugettext_lazy("Select a manager")))
		currentUserOrganisationId = 1
		if Session.objects.all()[0].session_key:
			currentUserOrganisationId = FMSUser.objects.get(pk=getLoggedInUserId(Session.objects.all()[0].session_key)).organisation
		managers = FMSUser.objects.filter(manager=True)
		managers = managers.filter(organisation_id=currentUserOrganisationId)

		for manager in managers:
			choices.append((manager.pk,manager.first_name+manager.last_name))

		super(ManagersChoiceField,self).__init__(choices,*args,**kwargs)

	def clean(self, value):
		super(ManagersChoiceField,self).clean(value)
		try:
			model = FMSUser.objects.get(pk=value)
		except FMSUser.DoesNotExist:
			raise ValidationError(self.error_messages['invalid_choice'])
		return model


class ManagersListForm(forms.Form):
	manager=ManagersChoiceField(label="")