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
    path("search/", search_property, name="search_property"),
    # -------------CREATE---------------
    path("register/", registerPage, name="register"),
    path("properties/create/", CreatePropertyView.as_view(), name="create_property"),
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
    path(
        "properties/<int:pk>/delete/",
        PropertyDeleteView.as_view(),
        name="delete_property",
    ),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
