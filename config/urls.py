from django.contrib import admin
from app.views import *
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", loginPage, name="login"),
    path("logout/", logoutUser, name="logout"),
    path("contract/", contractView, name="contract"),
    path("contact/", contact_view, name="contact"),
    path("payment-portal/", PaymentPortal, name="payment_portal"),
    path("manager/", ManagerInterfaceView.as_view(), name="manager_interface"),
    # -------------CREATE---------------
    path("register/", registerPage, name="register"),
    # -------------READ---------------
    path("", HomePageView.as_view(), name="home"),
    path("properties/", PropertiesView.as_view(), name="properties"),
    path(
        "profile/<int:pk>/", UserProfileDetailView.as_view(), name="user_profile_detail"
    ),
    # -------------UPDATE---------------
    path(
        "properties/<int:pk>/update/",
        UpdatePropertyView.as_view(),
        name="update_property",
    ),
    # -------------DELETE---------------
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
