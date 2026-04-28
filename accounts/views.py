from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib import messages
from django.db.models import Q
from django.core.files.base import ContentFile
from .models import Customer
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import base64
import json
from .forms import BusinessProfileForm
from documents.models import Document
from .models import ContactMessage, Notification
from decimal import Decimal
from django.utils import timezone
from accounts.utils import log_activity
from .models import BusinessProfile, Lead, ActivityLog

User = get_user_model()


# ---------------- HOME ----------------
def home(request):
    return render(request, "home.html")


# ---------------- LOGIN ----------------
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("username")   # frontend field name unchanged
        password = request.POST.get("password")
        selected_role = request.POST.get("role")

        if not selected_role:
            return render(request, "auth/login.html", {
                "error": "Please select Admin or Customer"
            })

        user_obj = User.objects.filter(email=email).first()

        if user_obj:
            user = authenticate(
                request,
                username=user_obj.username,
                password=password
            )
        else:
            user = None

        if not user:
            return render(request, "auth/login.html", {
                "error": "Invalid email or password"
            })

        if user.role != selected_role:
            return render(request, "auth/login.html", {
                "error": f"You are not allowed to login as {selected_role.capitalize()}"
            })

        login(request, user)

        log_activity(
            actor=user,
            action="Logged in"
        )

        return redirect(
            "accounts:admin_dashboard"
            if user.role == "admin"
            else "accounts:customer_dashboard"
        )

    return render(request, "auth/login.html")
# ---------------- LOGOUT ----------------
def logout_view(request):
    if request.user.is_authenticated:
        log_activity(
            actor=request.user,
            action="Logged out"
        )
    logout(request)
    return redirect("accounts:login")
# ---------------- REGISTER (ADMIN) ----------------
def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")

        if User.objects.filter(username=username).exists():
            return render(request, "auth/register.html", {
                "error": "Username already exists"
            })

        if User.objects.filter(email=email).exists():
            return render(request, "auth/register.html", {
                "error": "Email already exists"
            })

        if not mobile or not mobile.isdigit() or len(mobile) != 10:
            return render(request, "auth/register.html", {
                "error": "Enter a valid 10-digit mobile number"
            })

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            role="admin",
            is_staff=True,
            is_superuser=False
        )

        BusinessProfile.objects.create(
            user=user,
            mobile=mobile
        )

        log_activity(
            actor=user,
            action="Admin account created"
        )

        messages.success(request, "Admin account created successfully.")
        return redirect("accounts:login")

    return render(request, "auth/register.html")

# ---------------- ADMIN DASHBOARD ----------------
@login_required
def admin_dashboard(request):
    if request.user.role != "admin":
        messages.error(request, "Access denied.")
        return redirect("accounts:login")

    # ONLY customers created by this admin
    profiles = BusinessProfile.objects.filter(
        user__role="customer",
        created_by=request.user
    ).select_related("user")

    # ==============================
    # SERIALIZE NOTIFICATIONS FOR JSON
    # ==============================
    raw_notifications = Notification.objects.filter(
        receiver=request.user
    ).select_related("sender", "receiver").order_by("-created_at")
    notifications = [
        {
            "id": n.id,
            "sender": n.sender.username if n.sender else None,
            "recipient": n.receiver.username if n.receiver else None,
            "message": n.message,
            "is_read": n.is_read,
            "time": n.created_at.strftime("%b %d, %Y %I:%M %p"),

            "message_type": getattr(n, "message_type", None),
            "is_sent_reply": getattr(n, "is_sent_reply", False),
            "is_received_reply": getattr(n, "is_received_reply", False),

            "replied_to": getattr(n, "replied_to", None),
            "last_reply_message": getattr(n, "last_reply_message", None),
            "last_reply_sender": getattr(n, "last_reply_sender", None),
            "last_reply_target": getattr(n, "last_reply_target", None),

            "last_reply_time": (
                n.last_reply_time.strftime("%b %d, %Y %I:%M %p")
                if getattr(n, "last_reply_time", None)
                else None
            ),
        }
        for n in raw_notifications
    ]

    unread_count = raw_notifications.filter(is_read=False).count()

    # ==============================
    # CREATE CUSTOMER
    # ==============================
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("accounts:admin_dashboard")

        if not mobile or not mobile.isdigit() or len(mobile) != 10:
            messages.error(request, "Enter a valid 10-digit mobile number.")
            return redirect("accounts:admin_dashboard")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role="customer"
        )

        Customer.objects.create(
            user=user,
            mobile=mobile
        )

        BusinessProfile.objects.create(
            user=user,
            created_by=request.user,
            mobile=mobile
        )

        log_activity(
            actor=request.user,
            customer=user,
            action="Created customer"
        )

        messages.success(request, "Customer created successfully.")
        return redirect("accounts:admin_dashboard")

    return render(
        request,
        "admin/dashboard.html",
        {
            "profiles": profiles,
            "notifications": notifications,
            "unread_count": unread_count,
        }
    )
# ---------------- ADMIN VIEW CUSTOMER ----------------
@login_required  
def view_customer(request, user_id):
    if request.user.role != "admin":
        messages.error(request, "Access denied.")
        return redirect("accounts:login")

    customer_profile = get_object_or_404(
        Customer,
        user__id=user_id
    )

    customer_user = customer_profile.user

    profile = get_object_or_404(
        BusinessProfile,
        user=customer_user,
        created_by=request.user
    )

    documents = Document.objects.filter(
        user=customer_user
    ).order_by("-created_at")

    log_activity(
        actor=request.user,
        customer=customer_user,
        action=f"Viewed customer: {customer_user.username}"
    )

    return render(
        request,
        "admin/view_customer.html",
        {
            "profile": profile,
            "customer": customer_profile,
            "customer_user": customer_user,
            "documents": documents,
        }
    )

# ---------------- ADMIN PROFILE ----------------
@login_required
def admin_profile(request):
    user = request.user
    profile, _ = BusinessProfile.objects.get_or_create(user=user)

    if request.method == "POST":
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")

        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        profile_updated = False
        password_updated = False

        if email and email != user.email:
            user.email = email
            profile_updated = True

        if mobile and mobile.isdigit() and len(mobile) == 10:
            profile.mobile = mobile
            profile_updated = True

        if "profile_photo" in request.FILES:
            user.profile_photo = request.FILES["profile_photo"]
            profile_updated = True

        cropped_image = request.POST.get("cropped_image")
        if cropped_image:
            fmt, imgstr = cropped_image.split(";base64,")
            ext = fmt.split("/")[-1]
            user.profile_photo = ContentFile(
                base64.b64decode(imgstr),
                name=f"profile_{user.id}.{ext}"
            )
            profile_updated = True

        if current_password or new_password or confirm_password:
            if not user.check_password(current_password):
                messages.error(request, "Current password incorrect")
                return redirect("accounts:admin_profile")

            if new_password != confirm_password:
                messages.error(request, "Passwords do not match")
                return redirect("accounts:admin_profile")

            user.set_password(new_password)
            update_session_auth_hash(request, user)
            password_updated = True

        user.save()
        profile.save()

        if profile_updated:
            log_activity(
                actor=request.user,
                action="Updated admin profile"
            )

        if password_updated:
            log_activity(
                actor=request.user,
                action="Changed admin password"
            )

        messages.success(request, "Profile updated successfully")
        return redirect("accounts:admin_profile")

    return render(
        request,
        "admin/admin_profile.html",
        {
            "profile": user,
            "business": profile,
        }
    )
# ---------------- LEADS ----------------
@login_required
def leads_list(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")

        if Lead.objects.filter(email=email).exists():
            messages.error(request, "Lead with this email already exists.")
        else:
            Lead.objects.create(username=username, email=email)

            log_activity(
                actor=request.user,
                action="Created lead"
            )

            messages.success(request, "Lead added successfully.")

        return redirect("accounts:leads")

    leads = Lead.objects.all().order_by("-created_at")
    return render(request, "admin/leads.html", {"leads": leads})
@login_required
def delete_lead(request, lead_id):
    if request.user.role != "admin":
        messages.error(request, "Access denied.")
        return redirect("accounts:login")

    lead = get_object_or_404(Lead, id=lead_id)

    log_activity(
        actor=request.user,
        action="Deleted lead"
    )

    lead.delete()
    messages.success(request, "Lead deleted successfully.")
    return redirect("accounts:leads")
# ---------------- CONVERT LEAD ----------------
@login_required
def convert_lead(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)

    if request.method == "POST":
        user = User.objects.create_user(
            username=request.POST.get("new_username"),
            email=request.POST.get("email"),
            password=request.POST.get("password"),
            role="customer"
        )

        Customer.objects.create(
            user=user,
            mobile=request.POST.get("mobile", "")
        )

        BusinessProfile.objects.create(
            user=user,
            created_by=request.user
        )
        log_activity(
            actor=request.user,
            customer=user,
            action="Converted lead to customer"
        )

        lead.delete()
        messages.success(request, "Lead converted successfully.")
        return redirect("accounts:admin_dashboard")

    return render(request, "admin/convert_lead.html", {"lead": lead})
# ---------------- DELETE CUSTOMER ----------------
@login_required
def delete_customer(request, user_id):
    if request.user.role != "admin":
        messages.error(request, "Access denied.")
        return redirect("accounts:login")

    customer_user = get_object_or_404(User, id=user_id)

    if customer_user.role != "customer":
        messages.error(request, "This user is not a customer.")
        return redirect("accounts:admin_dashboard")

    log_activity(
        actor=request.user,
        customer=customer_user,
        action=f"Deleted customer: {customer_user.username}"
    )

    customer_user.delete()  # cascades to Customer, Profile, Documents
    messages.success(request, "Customer deleted successfully.")

    return redirect("accounts:admin_dashboard")
# ---------------- ADMIN HISTORY ----------------
@login_required
def admin_history(request):
    if request.user.role != "admin":
        return redirect("accounts:login")

    customer_ids = BusinessProfile.objects.filter(
        created_by=request.user
    ).values_list("user_id", flat=True)

    logs = (
        ActivityLog.objects
        .select_related("actor", "customer")
        .filter(
            Q(actor=request.user) |
            Q(customer_id__in=customer_ids)
        )
        .order_by("-created_at")[:100]
    )

    return render(request, "admin/history.html", {"logs": logs})
# ---------------- HELP ----------------
@login_required
def admin_help(request):
    if request.user.role != "admin":
        return redirect("accounts:login")
    return render(request, "admin/help.html")


# ---------------- TERMS ----------------
@login_required
def admin_terms(request):
    if request.user.role != "admin":
        return redirect("accounts:login")
    return render(request, "admin/terms.html")
# ---------------- CUSTOMER BUSINESS PROFILE ----------------
@login_required
def customer_business_profile(request):
    if request.user.role != "customer":
        messages.error(request, "Access denied.")
        return redirect("accounts:login")

    profile, _ = BusinessProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = BusinessProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()

            log_activity(
                actor=request.user,
                customer=request.user,
                action="Updated business profile"
            )

            messages.success(request, "Business profile updated successfully!")
            return redirect("accounts:customer_business_profile")
    else:
        form = BusinessProfileForm(instance=profile)

    return render(
        request,
        "customer/business_profile.html",
        {
            "form": form,
            "profile": profile
        }
    )
@login_required
def customer_profile(request):
    user = request.user
    profile, _ = Customer.objects.get_or_create(user=user)

    if request.method == "POST":
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")

        if email:
            user.email = email
            user.save(update_fields=["email"])

        if mobile:
            profile.mobile = mobile
            profile.save(update_fields=["mobile"])

        cropped_image = request.POST.get("cropped_image")
        if cropped_image:
            fmt, imgstr = cropped_image.split(";base64,")
            ext = fmt.split("/")[-1]
            profile.profile_photo.save(
                f"profile_{user.id}.{ext}",
                ContentFile(base64.b64decode(imgstr)),
                save=True
            )

        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if current_password and new_password and confirm_password:
            if not user.check_password(current_password):
                messages.error(
                    request,
                    "Current password is incorrect",
                    extra_tags="profile"
                )
                return redirect("accounts:customer_profile")

            if new_password != confirm_password:
                messages.error(
                    request,
                    "Passwords do not match",
                    extra_tags="profile"
                )
                return redirect("accounts:customer_profile")

            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)

            log_activity(
                actor=request.user,
                customer=request.user,
                action="Changed password"
            )

            messages.success(
                request,
                "Password updated successfully",
                extra_tags="profile"
            )
            return redirect("accounts:customer_profile")

        log_activity(
            actor=request.user,
            customer=request.user,
            action="Updated profile"
        )

        messages.success(
            request,
            "Profile updated successfully",
            extra_tags="profile"
        )
        return redirect("accounts:customer_profile")

    return render(
        request,
        "customer/customer_profile.html",
        {"profile": profile}
    )
@login_required
def customer_history(request):
    if request.user.role != "customer":
        messages.error(request, "Access denied.")
        return redirect("accounts:login")

    history = ActivityLog.objects.filter(
    actor=request.user
).order_by("-created_at")

    return render(
        request,
        "customer/history.html",
        {"history": history}
    )
@login_required
def admin_send_message(request, user_id):
    if request.user.role != "admin":
        messages.error(request, "Access denied.")
        return redirect("accounts:login")

    customer = get_object_or_404(
        User,
        id=user_id,
        role="customer"
    )

    if request.method == "POST":
        message_text = request.POST.get("message", "").strip()

        if not message_text:
            messages.error(request, "Message cannot be empty.")
            return redirect("accounts:admin_send_message", user_id=customer.id)

        # =====================================
        # SEND TO CUSTOMER
        # =====================================
        Notification.objects.create(
            sender=request.user,
            receiver=customer,
            message=message_text
        )

        # =====================================
        # SAVE COPY FOR ADMIN HISTORY/NOTIFICATIONS
        # =====================================
        Notification.objects.create(
            sender=request.user,
            receiver=request.user,
            message=f"You sent to {customer.username}: {message_text}"
        )

        # =====================================
        # ACTIVITY LOG
        # =====================================
        log_activity(
            actor=request.user,
            customer=customer,
            action="Sent message to customer"
        )

        # =====================================
        # SUCCESS MESSAGE
        # =====================================
        messages.success(
            request,
            f"✅ Message sent to {customer.username} successfully!"
        )

        return redirect(
            "accounts:view_customer",
            user_id=customer.id
        )

    return render(
        request,
        "admin/send_message.html",
        {
            "customer": customer
        }
    )
@login_required
@require_POST
def send_reply(request):
    try:
        data = json.loads(request.body)
        notification_id = data.get("notification_id")
        message = data.get("message", "").strip()

        if not notification_id or not message:
            return JsonResponse(
                {"success": False, "error": "Missing data"},
                status=400
            )

        original_notification = Notification.objects.get(
            id=notification_id,
            receiver=request.user
        )

        admin_user = original_notification.sender

        # =====================================
        # SEND REPLY TO ADMIN
        # =====================================
        Notification.objects.create(
            sender=request.user,
            receiver=admin_user,
            message=message
        )
        Notification.objects.create(
            sender=request.user,
            receiver=request.user,
            message=f"You replied to {admin_user.username}: {message}"
        )

        # =====================================
        # UPDATE ORIGINAL NOTIFICATION THREAD INFO
        # =====================================
        original_notification.is_read = True
        original_notification.last_reply_message = message
        original_notification.last_reply_sender = request.user.username
        original_notification.last_reply_target = admin_user.username
        original_notification.last_reply_time = timezone.now()
        original_notification.save()

        # =====================================
        # LOG ACTIVITY
        # =====================================
        log_activity(
            actor=request.user,
            customer=request.user,
            action="Replied to admin"
        )

        return JsonResponse({
            "success": True,
            "message": "Reply sent successfully!"
        })

    except Notification.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Notification not found"},
            status=404
        )

    except Exception as e:
        return JsonResponse(
            {"success": False, "error": str(e)},
            status=500
        )
        
@login_required
def mark_all_notifications_read(request):
    """Mark all notifications of the logged-in user as read"""
    if request.method == 'POST':
        Notification.objects.filter(
            receiver=request.user,
            is_read=False
        ).update(is_read=True)

        return JsonResponse({'success': True})

    return JsonResponse({'success': False}, status=400)
@login_required
def customer_dashboard(request):
    if request.user.role != "customer":
        messages.error(request, "Access denied.")
        return redirect("accounts:login")

    business_profile, _ = BusinessProfile.objects.get_or_create(
        user=request.user
    )

    customer_profile, _ = Customer.objects.get_or_create(
        user=request.user
    )

    notification_qs = Notification.objects.filter(
        receiver=request.user
    ).select_related('sender').order_by("-created_at")[:5]

    notifications = [
        {
            "id": note.id,
            "sender": note.sender.username if note.sender else "Admin",
            "message": note.message,
            "time": note.created_at.strftime("%d %b %Y, %I:%M %p"),
            "is_read": note.is_read,

            "last_reply_message": note.last_reply_message,
            "last_reply_sender": note.last_reply_sender,
            "last_reply_target": note.last_reply_target,
            "last_reply_time": (
                note.last_reply_time.strftime("%d %b %Y, %I:%M %p")
                if note.last_reply_time else None
            ),
        }
        for note in notification_qs
    ]
    return render(
        request,
        "customer/dashboard.html",
        {
            "profile": business_profile,
            "customer": customer_profile,
            "user": request.user,
            "notifications": notifications
        }
    )
# ---------------- CUSTOMER HELP ----------------
@login_required
def customer_help(request):
    if request.user.role != "customer":
        messages.error(request, "Access denied.")
        return redirect("accounts:login")
    return render(request, "customer/help.html")


# ---------------- CUSTOMER TERMS ----------------
@login_required
def customer_terms(request):
    if request.user.role != "customer":
        messages.error(request, "Access denied.")
        return redirect("accounts:login")
    return render(request, "customer/terms.html")

@login_required
def contact_admin(request):
    if request.user.role != "customer":
        return redirect("accounts:login")

    # Get customer's admin
    profile = get_object_or_404(BusinessProfile, user=request.user)
    admin_user = profile.created_by

    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            try:
                # Save contact message
                ContactMessage.objects.create(customer=request.user, message=message)
                
                Notification.objects.create(
                    sender=request.user,        # Customer sending to admin
                    receiver=admin_user,        # Admin receives
                    message=f" {request.user.username}: {message[:50]}"
                )
                
             
                Notification.objects.create(
                    sender=request.user,        # Customer notifies self
                    receiver=request.user,      # Customer receives confirmation
                    message=f"You sent to {admin_user.username}: {message[:50]}"
                )
                
                messages.success(
                    request, 
                    f"Message sent successfully to {admin_user.username}! ✨"
                )
                
                
                return redirect('accounts:contact_admin')
                
            except Exception as e:
                messages.error(request, f"Error sending message: {str(e)}")
                return redirect('accounts:contact_admin')
    
    return render(
        request, 
        "customer/contact_admin.html",
        {"admin_user": admin_user}
    )
