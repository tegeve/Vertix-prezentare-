from django import forms
from django.conf import settings
from .models import PublicRequest

class PublicRequestForm(forms.ModelForm):
    # doar ca să existe în form și să putem afișa erori lângă câmp
    attachments = forms.FileField(required=False)

    class Meta:
        model = PublicRequest
        fields = ["email", "phone", "company", "company_cif", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6}),
        }

    def clean(self):
        cleaned = super().clean()

        files = self.files.getlist("attachments")
        max_size = getattr(settings, "MAX_UPLOAD_SIZE", 200 * 1024 * 1024)

        for f in files:
            if f.size > max_size:
                self.add_error("attachments", f"Fișierul {f.name} depășește limita de 200MB.")

        return cleaned
