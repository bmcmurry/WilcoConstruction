from django import forms
from django.forms import ModelForm, TextInput, PasswordInput
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the widget for the password fields to PasswordInput
        self.fields["password1"].widget = forms.PasswordInput()
        self.fields["password2"].widget = forms.PasswordInput()


class TenantForm(ModelForm):
    class Meta:
        model = Tenant
        fields = "__all__"
        exclude = [
            "person",
            "dateCreated",
            "currentBalance",
            "linkToProperty",
            "linkToBuiltinUser",
        ]


class CreateRentalPropertyForm(ModelForm):
    class Meta:
        model = RentalProperty
        fields = "__all__"
        exclude = ["isRented"]


class UpdatePropertyForm(ModelForm):
    class Meta:
        model = RentalProperty
        fields = "__all__"
        exclude = ["isRented"]
