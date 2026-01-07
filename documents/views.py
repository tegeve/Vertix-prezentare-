from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
import json
from django.core.serializers.json import DjangoJSONEncoder

from accounts.models import User
from .forms import DocumentCreateForm, DocumentDataForm
from .forms_dynamic import build_document_form, MaterialFormSet
from .models import Document, DocumentType
from .permissions import is_admin_or_manager, is_technician, can_close_document, can_edit_document, can_view_document
from .services.numbering import allocate_number


@login_required
def document_list(request):
    u = request.user

    # ---------------------------
    # Base queryset pe rol
    # ---------------------------
    if u.role in [User.Role.ADMIN, User.Role.MANAGER]:
        qs = Document.objects.select_related("doc_type", "client_user", "owner").prefetch_related("technicians")
    elif u.role == User.Role.TEHNICIAN:
        qs = Document.objects.filter(technicians=u).select_related("doc_type", "client_user", "owner").prefetch_related("technicians")
    else:
        # client: doar FINAL
        qs = Document.objects.filter(client_user=u, status=Document.Status.FINAL).select_related("doc_type", "client_user", "owner")

    # ---------------------------
    # Filtre
    # ---------------------------
    q = (request.GET.get("q") or "").strip()
    f_type = (request.GET.get("type") or "").strip()      # doc_type.code
    f_status = (request.GET.get("status") or "").strip()  # DRAFT/...
    per_page = int(request.GET.get("per_page") or 20)
    page = int(request.GET.get("page") or 1)

    if q:
        qs = qs.filter(
            Q(number__icontains=q) |
            Q(doc_type__name__icontains=q) |
            Q(client_user__email__icontains=q) |
            Q(client_user__company_name__icontains=q) |
            Q(owner__email__icontains=q)
        )

    if f_type:
        qs = qs.filter(doc_type__code=f_type)

    if f_status:
        qs = qs.filter(status=f_status)

    # ---------------------------
    # Sort
    # ---------------------------
    sort = request.GET.get("sort") or "created_at"
    direction = request.GET.get("dir") or "desc"

    sort_map = {
        "created_at": "created_at",
        "number": "number",
        "type": "doc_type__name",
        "status": "status",
        "client": "client_user__company_name",
        "owner": "owner__email",
    }
    order = sort_map.get(sort, "created_at")
    if direction == "desc":
        order = "-" + order

    qs = qs.order_by(order)

    # ---------------------------
    # Pagination + keep_qs
    # ---------------------------
    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(page)

    keep = request.GET.copy()
    keep.pop("page", None)
    keep_qs = keep.urlencode()

    doc_types = DocumentType.objects.filter(is_active=True).order_by("name")

    return render(request, "documents/list.html", {
        "page_obj": page_obj,
        "q": q,
        "f_type": f_type,
        "f_status": f_status,
        "per_page": per_page,
        "per_page_choices": [10, 20, 50, 100],
        "keep_qs": keep_qs,
        "sort": sort,
        "dir": direction,
        "doc_types": doc_types,
    })


@login_required
@require_POST
def document_delete(request, pk: int):
    doc = get_object_or_404(Document, pk=pk)
    if request.user.role not in [User.Role.ADMIN, User.Role.MANAGER]:
        raise Http404()

    number = doc.number
    doc.delete()
    messages.success(request, f"Document șters: {number}")
    return redirect("documents:list")



@login_required
def document_detail(request, pk: int):
    doc = get_object_or_404(Document.objects.select_related("doc_type", "client_user", "owner"), pk=pk)

    if not can_view_document(request.user, doc):
        raise Http404()

    return render(request, "documents/detail.html", {"doc": doc})


@login_required
def document_create(request):
    if not is_admin_or_manager(request.user):
        raise Http404()

    if request.method == "POST":
        form = DocumentCreateForm(request.POST)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.created_by = request.user
            if not doc.owner:
                doc.owner = request.user
            doc.number = allocate_number(doc.doc_type)
            doc.save()
            form.save_m2m()
            messages.success(request, f"Document creat: {doc.number}")
            return redirect("documents:detail", pk=doc.pk)
    else:
        form = DocumentCreateForm()

    return render(request, "documents/create.html", {"form": form})



@login_required
def document_edit(request, pk: int):
    doc = get_object_or_404(Document.objects.select_related("doc_type"), pk=pk)

    if not can_edit_document(request.user, doc):
        raise Http404()

    schema = doc.doc_type.schema_json or {}
    DynamicForm = build_document_form(schema)

    # date existente
    data = doc.data_json or {}
    materials_initial = data.get("materials") or []

    if request.method == "POST":
        form = DynamicForm(request.POST)
        materials_fs = MaterialFormSet(request.POST, prefix="materials")

        # add bootstrap classes for formset
        for f in materials_fs:
            f.add_bootstrap()

        if form.is_valid() and materials_fs.is_valid():
            # 1) datele din form (pot conține datetime)
            cleaned = form.cleaned_data

            # 2) materials din formset
            materials = []
            for row in materials_fs.cleaned_data:
                if not row:
                    continue
                if row.get("DELETE"):
                    continue
                materials.append({
                    "name": row.get("name", ""),
                    "qty": str(row.get("qty", "")),
                    "unit": row.get("unit", ""),
                    "notes": row.get("notes", ""),
                })

            cleaned["materials"] = materials

            # 3) convertim totul în JSON-safe (datetime/date/Decimal etc.)
            cleaned_safe = json.loads(json.dumps(cleaned, cls=DjangoJSONEncoder))

            # 4) salvăm
            doc.data_json = cleaned_safe
            doc.save(update_fields=["data_json"])

            messages.success(request, "Document salvat.")
            return redirect("documents:detail", pk=doc.pk)

            messages.success(request, "Document salvat.")
            return redirect("documents:detail", pk=doc.pk)
    else:
        form = DynamicForm(initial=data)
        materials_fs = MaterialFormSet(initial=materials_initial, prefix="materials")
        for f in materials_fs:
            f.add_bootstrap()

    # bootstrap classes pentru câmpuri simple
    for name, field in form.fields.items():
        cls = "form-control"
        if field.widget.__class__.__name__ in ["Select", "SelectMultiple"]:
            cls = "form-select"
        # mic în portal
        field.widget.attrs.setdefault("class", cls + " form-control-sm")

    return render(request, "documents/edit_work_order.html", {
        "doc": doc,
        "form": form,
        "materials_fs": materials_fs,
    })



@login_required
@require_POST
def document_close(request, pk: int):
    doc = get_object_or_404(Document, pk=pk)

    if not can_close_document(request.user, doc):
        raise Http404()

    doc.status = Document.Status.FINAL
    doc.save(update_fields=["status"])

    # In pasul 2: aici generam DOCX+PDF si salvam in doc.docx_file / doc.pdf_file
    messages.success(request, f"Document inchis: {doc.number}")
    return redirect("documents:detail", pk=doc.pk)

@login_required
def document_preview(request, pk: int):
    # încărcăm documentul
    doc = get_object_or_404(
        Document.objects.select_related("doc_type", "client_user", "owner"),
        pk=pk
    )

    # permisiuni
    if not can_view_document(request.user, doc):
        raise Http404()

    # termeni (editabili din Admin)
    from .services.terms import get_terms_for_doc
    terms = get_terms_for_doc(doc)

    return render(request, "documents/preview.html", {
        "doc": doc,
        "data": doc.data_json or {},
        "client": doc.client_user,
        "owner": doc.owner,
        "terms_title": terms.title if terms else "Termeni și condiții",
        "terms_html": terms.body_html if terms else "",
    })
