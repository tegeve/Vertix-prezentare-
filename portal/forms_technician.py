from django import forms
from .models import Technician

class TechnicianForm(forms.ModelForm):
    class Meta:
        model = Technician
        fields = ["name", "company_name", "company_cif", "email", "phone", "address", "category", "is_active"]
        widgets = {"address": forms.Textarea(attrs={"rows": 2})}
