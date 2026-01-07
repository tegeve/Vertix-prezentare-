from __future__ import annotations

from documents.models import DocumentTerms


def get_terms_for_doc(doc):
    """
    Returnează termenii pentru un document:
    - dacă DocumentType are terms setat => îl folosește
    - altfel, folosește DocumentTerms(key="default") activ, dacă există
    - altfel, primul activ
    - altfel None
    """
    # override pe doc_type
    if getattr(doc.doc_type, "terms_id", None):
        return doc.doc_type.terms

    # fallback: default activ
    t = DocumentTerms.objects.filter(key="default", is_active=True).first()
    if t:
        return t

    # fallback: primul activ
    return DocumentTerms.objects.filter(is_active=True).order_by("key").first()
