from django.urls import path
from . import views

app_name = "documents"

urlpatterns = [
    # LIST
    path("", views.document_list, name="list"),

    # CREATE
    path("create/", views.document_create, name="create"),

    # DETAIL
    path("<int:pk>/", views.document_detail, name="detail"),

    # EDIT (formular work_order)
    path("<int:pk>/edit/", views.document_edit, name="edit"),

    # PREVIEW (2 pagini A4: Ordin + Termeni)
    path("<int:pk>/preview/", views.document_preview, name="preview"),

    # CLOSE (FINAL)
    path("<int:pk>/close/", views.document_close, name="close"),

    # DELETE
    path("<int:pk>/delete/", views.document_delete, name="delete"),
]
