from django.urls import path
from . import views

app_name = "documents"

urlpatterns = [
    path("my-documents/", views.customer_documents, name="customer_documents"),
    path("admin/upload/<int:user_id>/", views.admin_upload_document, name="admin_upload_document"),
    path("admin/all/", views.admin_all_documents, name="admin_all_documents"),
]
