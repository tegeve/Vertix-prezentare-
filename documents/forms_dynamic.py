from __future__ import annotations

from django import forms
from django.forms import formset_factory
from django.utils.dateparse import parse_date, parse_datetime


def _field_from_schema(f: dict) -> forms.Field:
    ftype = f.get("type")
    required = bool(f.get("required", False))
    label = f.get("label", f.get("name", ""))

    if ftype == "text":
        return forms.CharField(label=label, required=required, max_length=500)

    if ftype == "textarea":
        return forms.CharField(label=label, required=required, widget=forms.Textarea(attrs={"rows": 3}))

    if ftype == "select":
        choices = [(c, c) for c in (f.get("choices") or [])]
        return forms.ChoiceField(label=label, required=required, choices=[("", "—")] + choices)

    if ftype == "number":
        return forms.DecimalField(label=label, required=required, max_digits=12, decimal_places=2)

    if ftype == "date":
        return forms.DateField(label=label, required=required, widget=forms.DateInput(attrs={"type": "date"}))

    if ftype == "datetime":
        # HTML input datetime-local (browser)
        return forms.DateTimeField(
            label=label,
            required=required,
            widget=forms.DateTimeInput(attrs={"type": "datetime-local"})
        )

    # fallback
    return forms.CharField(label=label, required=required, max_length=500)


def build_document_form(schema_json: dict) -> type[forms.Form]:
    """
    Construiește un Form Django din schema_json (fără câmpurile de tip table).
    """
    fields = {}
    for f in schema_json.get("fields", []):
        if f.get("type") == "table":
            continue
        name = f["name"]
        fields[name] = _field_from_schema(f)

    DynamicForm = type("DynamicDocumentForm", (forms.Form,), fields)
    return DynamicForm


class MaterialRowForm(forms.Form):
    name = forms.CharField(label="Denumire", required=True)
    qty = forms.DecimalField(label="Cant.", required=True, max_digits=12, decimal_places=2)
    unit = forms.CharField(label="UM", required=True, max_length=30)
    notes = forms.CharField(label="Observații", required=False, max_length=200)

    def add_bootstrap(self):
        for n, f in self.fields.items():
            f.widget.attrs.setdefault("class", "form-control form-control-sm")


MaterialFormSet = formset_factory(MaterialRowForm, extra=0, can_delete=True)
