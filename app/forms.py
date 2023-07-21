from django import forms
from django.forms import ModelForm
from .models import *
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]


class TenantForm(ModelForm):
    class Meta:
        model = Tenant
        fields = "__all__"
        exclude = ["person", "dateCreated", "currentBalance"]


class CreateRentalPropertyForm(ModelForm):
    class Meta:
        model = RentalProperty
        fields = "__all__"
        exclude = ["linkToTenant", "isRented"]
