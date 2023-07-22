from django.contrib import admin
from app.views import *
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomePageView.as_view(), name="home"),
    path(
        "profile/<int:pk>/", UserProfileDetailView.as_view(), name="user_profile_detail"
    ),
    path(
        "profile/<int:pk>/update/",
        UserProfileUpdateView.as_view(),
        name="user_profile_update",
    ),
    path("register/", registerPage, name="register"),
    path("login/", loginPage, name="login"),
    path("logout/", logoutUser, name="logout"),
    path("rent/", rentView, name="rent"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
