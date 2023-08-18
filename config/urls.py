from django.contrib import admin
from app.views import *
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", loginPage, name="login"),
    path("logout/", logoutUser, name="logout"),
    path("contact/", contact_view, name="contact"),
    path("payment-portal/", PaymentPortalView.as_view(), name="payment_portal"),
    path("payment_success/", PaymentSuccessView.as_view(), name="payment_success"),
    path("payment_fail/", PaymentFail, name="payment_fail"),
    path("stripe_webhook/", stripe_webhook, name="stripe_webhook"),
    # -------------PASSWORD/RESET-------------
    path(
        "reset_password/",
        auth_views.PasswordResetView.as_view(template_name="password_reset.html"),
        name="reset_password",
    ),
    path(
        "reset_password_sent/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="password_reset_sent.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="password_reset_form.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset_password_complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="password_reset_done.html"
        ),
        name="password_reset_complete",
    ),
    # -------------CREATE---------------
    path("register/", registerPage, name="register"),
    path("properties/create/", CreatePropertyView.as_view(), name="create_property"),
    path("lease/create/", CreateLeaseView.as_view(), name="create_lease"),
    path(
        "construction/create/",
        CreateConstructionView.as_view(),
        name="create_construction",
    ),
    # -------------READ---------------
    path("", HomePageView.as_view(), name="home"),
    path("properties/", PropertyView.as_view(), name="properties"),
    path("construction/", ConstructionView.as_view(), name="construction"),
    path("manager/", ManagerInterfaceView.as_view(), name="manager_interface"),
    path(
        "profile/<int:pk>/", UserProfileDetailView.as_view(), name="user_profile_detail"
    ),
    # -------------UPDATE---------------
    path(
        "properties/<int:pk>/update/",
        UpdatePropertyView.as_view(),
        name="update_property",
    ),
    path(
        "properties/<int:pk>/feature/",
        SetPropertyToFeaturedView.as_view(),
        name="feature_property",
    ),
    path(
        "construction/<int:pk>/update/",
        UpdateConstructionView.as_view(),
        name="update_construction",
    ),
    path(
        "construction/<int:pk>/feature/",
        SetConstructionToFeaturedView.as_view(),
        name="feature_construction",
    ),
    path(
        "lease/<int:pk>/update/",
        UpdateLeaseView.as_view(),
        name="update_lease",
    ),
    # -------------DELETE---------------
    path(
        "properties/<int:pk>/delete/",
        PropertyDeleteView.as_view(),
        name="delete_property",
    ),
    path(
        "photos/<int:pk>/delete/",
        PhotoDeleteView.as_view(),
        name="delete_photo",
    ),
    path(
        "construction/<int:pk>/delete/",
        ConstructionDeleteView.as_view(),
        name="delete_construction",
    ),
    path(
        "construction/photos/<int:pk>/delete/",
        ConstructionPhotoDeleteView.as_view(),
        name="delete_construction_photo",
    ),
    path(
        "lease/<int:pk>/delete/",
        LeaseDeleteView.as_view(),
        name="delete_lease",
    ),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
