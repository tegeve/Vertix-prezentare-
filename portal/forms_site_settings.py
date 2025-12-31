from django import forms
from website.models import SiteSettings

class SitePagesSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = [
            "home_enabled",
            "about_enabled",
            "services_enabled",
            "projects_enabled",
            "industries_enabled",
            "contact_enabled",
            "blog_enabled",
            "careers_enabled",
            "gdpr_enabled",
            "cookies_enabled",
        ]
        labels = {
            "home_enabled": "Acasă",
            "about_enabled": "Despre noi",
            "services_enabled": "Servicii",
            "projects_enabled": "Proiecte / Portofoliu",
            "industries_enabled": "Industrii",
            "contact_enabled": "Contact",
            "blog_enabled": "Blog / Noutăți",
            "careers_enabled": "Cariere",
            "gdpr_enabled": "GDPR",
            "cookies_enabled": "Cookies",
        }
