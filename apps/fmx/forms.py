from django import forms

class SeveralOccurencesForm(forms.Form):
    """Form to validate several_occurences"""

    several_occurences = forms.BooleanField(initial=False, label='several_occurences')