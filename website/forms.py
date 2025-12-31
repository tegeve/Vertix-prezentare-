from django import forms
from .models import ContactMessage, PopUpMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "company", "message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 5}),
        }

class PopUpMessageForm(forms.ModelForm):
    class Meta:
        model = PopUpMessage
        fields = [
            "title", "body", "style",
            "start_at", "end_at",
            "is_enabled",
            "show_once_per_browser",
            "show_on_home_only",
            "priority",
        ]
        widgets = {
            "start_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }