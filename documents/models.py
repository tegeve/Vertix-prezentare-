from django.conf import settings
from django.db import models
from django.utils import timezone

class DocumentType(models.Model):
    code = models.SlugField(unique=True)  # ex: work_order
    name = models.CharField(max_length=200)  # ex: Ordin de lucru
    is_active = models.BooleanField(default=True)

    # Schema pentru formular dinamic (pasul 3)
    schema_json = models.JSONField(default=dict, blank=True)

    # Template-uri (pasul 2)
    docx_template = models.FileField(upload_to="doc_templates/docx/", blank=True, null=True)
    html_template = models.TextField(blank=True)

    # Numerotare
    series = models.CharField(max_length=20, default="DOC")   # ex: OL, PV, SR
    next_number = models.PositiveIntegerField(default=1)
    terms = models.ForeignKey(
        "documents.DocumentTerms",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="document_types",
        help_text="Dacă e setat, pagina 2 va folosi acești termeni. Dacă nu, folosește 'default'."
    )

    def __str__(self):
        return f"{self.name} ({self.code})"


class Document(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        IN_PROGRESS = "IN_PROGRESS", "In lucru"
        READY = "READY", "Pregatit"
        FINAL = "FINAL", "Inchis (Final)"
        CANCELLED = "CANCELLED", "Anulat"

    doc_type = models.ForeignKey("documents.DocumentType", on_delete=models.PROTECT, related_name="documents")
    number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)

    client_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="client_documents"
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="owned_documents"
    )

    technicians = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="assigned_documents"
    )

    data_json = models.JSONField(default=dict, blank=True)

    docx_file = models.FileField(upload_to="generated_docs/docx/", blank=True, null=True)
    pdf_file = models.FileField(upload_to="generated_docs/pdf/", blank=True, null=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="created_documents"
    )
    created_at = models.DateTimeField(default=timezone.now)

    def is_closed(self) -> bool:
        return self.status in {self.Status.FINAL, self.Status.CANCELLED}

    def __str__(self):
        return f"{self.number} - {self.doc_type.name}"



class DocumentTerms(models.Model):
    key = models.SlugField(unique=True)  # ex: "default"
    title = models.CharField(max_length=200, default="Termeni și condiții")
    body_html = models.TextField(help_text="HTML permis (paragrafe, liste). Se va afișa ca pagina 2.")
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Termeni document"
        verbose_name_plural = "Termeni documente"

    def __str__(self):
        return f"{self.key} ({'activ' if self.is_active else 'inactiv'})"
