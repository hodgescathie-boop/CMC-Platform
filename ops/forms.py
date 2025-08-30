from django import forms
from .models import Estimate

class EstimateForm(forms.ModelForm):
    within_radius = forms.BooleanField(
        required=False,
        label="I am within ~30 miles of 35055",
        help_text="If you're outside, please submit and our office will contact you with options."
    )

    class Meta:
        model = Estimate
        fields = [
            "name", "email", "phone", "address", "zip_code",
            "service_type", "frequency", "hours", "addons", "within_radius"
        ]
        widgets = {
            "addons": forms.CheckboxSelectMultiple,
        }
