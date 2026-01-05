from django import forms
from .models import Ticket
from website.models import SiteSettings
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3


import time

from .models_chat import TicketMessage


class TicketCreateForm(forms.ModelForm):
    # anti-bot
    website = forms.CharField(required=False)  # honeypot
    started_at = forms.IntegerField(required=False, widget=forms.HiddenInput)

    # reCAPTCHA v3 (invizibil)
    captcha = ReCaptchaField(widget=ReCaptchaV3)

    class Meta:
        model = Ticket
        fields = ["subject", "message", "started_at", "website", "captcha"]
        widgets = {"message": forms.Textarea(attrs={"rows": 6})}

    def clean_website(self):
        # dacă e completat => bot
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("Spam detectat.")
        return ""

    def clean(self):
        cleaned = super().clean()
        started_at = cleaned.get("started_at") or 0

        now = int(time.time())

        # completare prea rapidă => bot
        if started_at and (now - int(started_at) < 4):
            raise forms.ValidationError("Trimitere prea rapidă. Reîncearcă.")
        return cleaned


class SitePagesSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = [
            "home_enabled","about_enabled","services_enabled","projects_enabled",
            "industries_enabled","contact_enabled","blog_enabled","careers_enabled",
            "gdpr_enabled","cookies_enabled",
        ]


class TicketMessageForm(forms.ModelForm):
    class Meta:
        model = TicketMessage
        fields = ["body", "reply_to", "visibility"]

    def clean_visibility(self):
        v = self.cleaned_data["visibility"]
        # clientul nu are voie la INTERNAL
        user = getattr(self, "user", None)
        if user and getattr(user, "role", None) == "CLIENT" and v == "INTERNAL":
            return TicketMessage.Visibility.PUBLIC
        return v
