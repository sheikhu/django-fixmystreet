from django import forms

class SeveralOccurencesForm(forms.Form):
    """Form to validate several_occurences"""

    several_occurences = forms.BooleanField(initial=False, label='several_occurences')

class IsIncidentCreationForm(forms.Form):
    """Form to validate that we are in incident creation process"""

    is_incident_creation = forms.BooleanField(initial=False, label='is_incident_creation')