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


class CreatePropertyForm(ModelForm):
    class Meta:
        model = RentalProperty
        fields = "__all__"
        exclude = ["isRented", "isFeaturedProperty"]

    def clean(self):
        cleaned_data = super().clean()
        address = cleaned_data.get("address")
        city = cleaned_data.get("city")

        # Check if a property with the same address and city already exists
        if address and city:
            existing_property = RentalProperty.objects.filter(
                address=address, city=city
            ).exists()
            if existing_property:
                raise forms.ValidationError(
                    f"A property with the address {address} in the city {city} already exists and can't be duplicated."
                )

        return cleaned_data


class PropertyPhotoForm(ModelForm):
    class Meta:
        model = PropertyPhoto
        fields = "__all__"
        exclude = ["propertyOfImage"]


class ContactForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField(widget=forms.EmailInput(attrs={"type": "email"}))
    CHOICES = (
        ("Rentals", "Rentals"),
        ("Contracts", "Contracts"),
        ("Other", "Other"),
    )

    categories = forms.ChoiceField(choices=CHOICES)
    phone = forms.CharField(max_length=20)
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)


class QuoteForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField(widget=forms.EmailInput(attrs={"type": "email"}))
    CHOICES = (
        ("Residential", "Residential"),
        ("Commercial", "Commercial"),
        ("Other", "Other"),
    )

    categories = forms.Select(choices=CHOICES)

    phone = forms.CharField(max_length=20)
    subject = forms.CharField(max_length=100)

    message = forms.CharField(widget=forms.Textarea)


class PropertySearchForm(forms.Form):
    SEARCH_CHOICES = [
        ("address", "Address"),
        ("city", "City"),
        ("isRented", "isRented"),
        ("price", "price"),
        ("squareFoot", "squareFoot"),
        ("bedrooms", "bedrooms"),
        ("bathrooms", "bathrooms"),
        ("isPetFriendly", "isPetFriendly"),
    ]

    search_field = forms.ChoiceField(choices=SEARCH_CHOICES, label="Search Field")
    search_query = forms.CharField(label="Search Query", max_length=100)
