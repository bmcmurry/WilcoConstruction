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
            "slug",
            "person",
            "dateCreated",
            "currentBalance",
            "linkToBuiltinUser",
        ]


class LeaseForm(forms.ModelForm):
    selected_tenant = forms.ModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Lease
        fields = [
            "pricePerMonth",
            "isLate",
            "lateFee",
            "startDate",
            "endDate",
            "linkToProperty",
            "currentBalance",
        ]
        exclude = ["slug", "dueDate"]
        widgets = {
            "startDate": forms.DateInput(attrs={"type": "date"}),
            "endDate": forms.DateInput(attrs={"type": "date"}),
        }


class CreatePropertyForm(ModelForm):
    class Meta:
        model = RentalProperty
        fields = "__all__"
        exclude = ["isRented", "isFeaturedProperty", "slug"]

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


class UpdatePropertyForm(ModelForm):
    class Meta:
        model = RentalProperty
        fields = "__all__"
        exclude = ["isRented", "isFeaturedProperty", "slug"]


class PropertyPhotoForm(ModelForm):
    class Meta:
        model = PropertyPhoto
        fields = "__all__"
        exclude = ["propertyOfImage", "slug"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["picture"].required = False


class CreateConstructionForm(ModelForm):
    class Meta:
        model = ConstructionJob
        fields = "__all__"
        exclude = ["dateCreated", "isFeaturedConstruction", "slug"]


class ConstructionPhotoForm(ModelForm):
    class Meta:
        model = ConstructionJobPhoto
        fields = "__all__"
        exclude = ["constructionOfImage", "slug"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["picture"].required = False


class ContactForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField(widget=forms.EmailInput(attrs={"type": "email"}))
    # CHOICES = (
    #     ("Rentals", "Rentals"),
    #     ("Construction", "Construction"),
    #     ("Other", "Other"),
    # )

    # categories = forms.ChoiceField(choices=CHOICES)
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

    categories = forms.ChoiceField(choices=CHOICES)
    phone = forms.CharField(max_length=20)
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)
