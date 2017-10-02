from django import forms

class SeveralOccurencesForm(forms.Form):
    """Form to validate several_occurences"""

    several_occurences = forms.BooleanField(initial=False, label='several_occurences')

class IsIncidentCreationForm(forms.Form):
    """Form to validate that we are in incident creation process"""

    is_incident_creation = forms.BooleanField(initial=False, label='is_incident_creation')

class IsProForm(forms.Form):
    """Form to validate that we have a pro asking for duplicates"""

    pro = forms.BooleanField(initial=False, label='is_pro')

class AddMobileUpdateNotificationForm(forms.Form):
    """Form to validate that we have must add a notification in the creation mail"""

    mobile_notification = forms.BooleanField(initial=False, label='mobile_notification')