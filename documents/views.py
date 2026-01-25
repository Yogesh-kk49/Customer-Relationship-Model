from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from accounts.models import ActivityLog
from .models import Document
from accounts.models import ActivityLog, Notification, BusinessProfile

User = get_user_model()


# ===============================
# CUSTOMER: VIEW & UPLOAD DOCUMENTS
# ===============================
@login_required
def customer_documents(request):
    if request.user.role != "customer":
        messages.error(request, "Access denied.")
        return redirect("accounts:login")

    if request.method == "POST":
        # 1️⃣ Save document
        document = Document.objects.create(
            user=request.user,
            uploaded_by=request.user,
            document_type=request.POST.get("document_type"),
            title=request.POST.get("title"),
            document_file=request.FILES.get("document_file"),
            document_date=request.POST.get("document_date") or None,
            description=request.POST.get("description", "")
        )

        # 2️⃣ Activity log (HISTORY) ✅ KEEP THIS
        ActivityLog.objects.create(
            actor=request.user,
            customer=request.user,
            action=f"Uploaded document: {document.title}"
        )

        # 3️⃣ Find assigned admin
        profile = get_object_or_404(BusinessProfile, user=request.user)
        admin_user = profile.created_by

        # 4️⃣ Notification for admin 🔔
        if admin_user:
            Notification.objects.create(
                sender=request.user,
                receiver=admin_user,
                message=f"📄 {request.user.username} uploaded a document: {document.title}"
            )

        messages.success(request, "Document uploaded successfully.")
        return redirect("documents:customer_documents")

    documents = Document.objects.filter(user=request.user).order_by("-created_at")

    return render(
        request,
        "documents/customer_upload_documents.html",
        {"documents": documents}
    )

# ===============================
# ADMIN: UPLOAD DOCUMENT FOR CUSTOMER
# ===============================
@login_required
def admin_upload_document(request, user_id):
    if request.user.role != "admin":
        messages.error(request, "Access denied.")
        return redirect("accounts:login")

    customer = get_object_or_404(User, id=user_id, role="customer")

    if request.method == "POST":
        Document.objects.create(
            user=customer,
            uploaded_by=request.user,
            document_type=request.POST.get("document_type"),
            title=request.POST.get("title"),
            document_file=request.FILES.get("document_file"),
            document_date=request.POST.get("document_date") or None,
            description=request.POST.get("description", "")
        )
        messages.success(request, "Document uploaded for customer.")
        return redirect("accounts:view_customer", user_id=customer.id)

    documents = Document.objects.filter(user=customer).order_by("-created_at")

    return render(
        request,
        "documents/admin_upload_documents.html",
        {
            "customer": customer,
            "documents": documents
        }
    )


# ===============================
# ADMIN: VIEW ALL DOCUMENTS
# ===============================
@login_required
def admin_all_documents(request):
    if request.user.role != "admin":
        messages.error(request, "Access denied.")
        return redirect("accounts:login")

    documents = Document.objects.select_related(
        "user", "uploaded_by"
    ).order_by("-created_at")

    return render(
        request,
        "documents/admin_all_documents.html",
        {"documents": documents}
    )
