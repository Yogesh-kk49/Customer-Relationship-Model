from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static

def home(request):
    return render(request, "home.html")  

def health_check(request):
    """Lightweight endpoint for uptime/keep-alive pings. No DB hits, no templates."""
    return HttpResponse("OK", content_type="text/plain")

urlpatterns = [
    path("", home, name="home"),
    path("health/", health_check, name="health_check"),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("documents/", include("documents.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)