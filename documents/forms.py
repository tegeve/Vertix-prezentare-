from django import forms
from accounts.models import User
from .models import Document, DocumentType

class DocumentCreateForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["doc_type", "client_user", "owner", "technicians"]

    doc_type = forms.ModelChoiceField(
        queryset=DocumentType.objects.filter(is_active=True),
        required=True
    )

    client_user = forms.ModelChoiceField(
        queryset=User.objects.filter(role=User.Role.CLIENT, is_active=True),
        required=False
    )

    owner = forms.ModelChoiceField(
        queryset=User.objects.filter(role__in=[User.Role.ADMIN, User.Role.MANAGER], is_active=True),
        required=False
    )

    technicians = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(role=User.Role.TEHNICIAN, is_active=True),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )


class DocumentDataForm(forms.Form):
    """
    Temporar (pas intermediar): un camp JSON text.
    In pasul 3 facem UI din schema_json (form dinamic).
    """
    data_json = forms.JSONField(required=False)
    status = forms.ChoiceField(choices=Document.Status.choices, required=True)
