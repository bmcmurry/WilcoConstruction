from django.contrib import admin
from app.views import *
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomePageView.as_view(), name="home"),
    path("register/", registerPage, name="register"),
    path("login/", loginPage, name="login"),
    path("logout/", logoutUser, name="logout"),
    path("rent/", rentView, name="rent"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
