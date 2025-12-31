from django import forms
from .models import RequestStatus

class RequestStatusForm(forms.ModelForm):
    class Meta:
        model = RequestStatus
        fields = ["name", "order", "is_active"]
