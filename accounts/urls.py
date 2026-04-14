from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # AUTH
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),

    # HOME
    path("", views.home, name="home"),

    # ADMIN AREA (❌ NOT under /admin/)
    path("dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("leads/", views.leads_list, name="leads"),
    path("profile/", views.admin_profile, name="admin_profile"),
    path("customer/<int:user_id>/", views.view_customer, name="view_customer"),
    path("delete-customer/<int:user_id>/", views.delete_customer, name="delete_customer"),
    path(
        "leads/convert/<int:lead_id>/",
        views.convert_lead,
        name="convert_lead"
    ),
    path("dashboard/history/", views.admin_history, name="admin_history"),
    path("dashboard/help/", views.admin_help, name="admin_help"),
    path("dashboard/terms/", views.admin_terms, name="admin_terms"),


    # CUSTOMER AREA
    path("customer/dashboard/", views.customer_dashboard, name="customer_dashboard"),
    path("leads/delete/<int:lead_id>/", views.delete_lead, name="delete_lead"),
    path(
    "customer/business-profile/",
    views.customer_business_profile,
    name="customer_business_profile"
),
    path("customer/profile/", views.customer_profile, name="customer_profile"),
    path(
    "customer/history/",
    views.customer_history,
    name="customer_history"
),
    path(
    "admin/send-message/<int:user_id>/",
    views.admin_send_message,
    name="admin_send_message"
),
    path('send-reply/', views.send_reply, name='send_reply'),
    path('mark-all-notifications-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path("customer/help/", views.customer_help, name="customer_help"),
    path("customer/terms/", views.customer_terms, name="customer_terms"),
    path("contact-admin/", views.contact_admin, name="contact_admin"),

]
