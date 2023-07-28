from django.shortcuts import render, redirect
from django.forms import inlineformset_factory
from django.views.generic import TemplateView, UpdateView, DetailView, CreateView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator


from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.admin.views.decorators import staff_member_required

from .forms import *
from .models import *
from .decorators import *

from django.contrib.auth.models import Group
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views import View

from django.core.mail import send_mail

import smtplib

## --------------LOGIN/LOGOUT/REGISTER----------------##


@unauthenticated_user
def registerPage(request):
    context = {}
    form = CreateUserForm()

    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save(
                commit=False
            )  # Create a user instance without saving to the database yet
            user.first_name = form.cleaned_data.get("first_name")
            user.last_name = form.cleaned_data.get("last_name")
            user.save()

            group = Group.objects.get(name="tenants")
            user.groups.add(group)
            Tenant.objects.create(
                linkToBuiltinUser=user,
                first_name=user.first_name,
                last_name=user.last_name,
                userEmail=user.email,
            )
            login(request, user)
            return redirect("home")

        else:
            errors = form.errors.as_data()
            error_messages = {}
            for field, error_list in errors.items():
                error_messages[field] = [error.message for error in error_list]

            context["form"] = form  # Add the form to the context
            context[
                "error_messages"
            ] = error_messages  # Add error_messages to the context

    context["form"] = form  # Add the form to the context even if it's a GET request
    return render(request, "register.html", context)


def loginPage(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                if request.user.is_superuser:
                    return redirect("manager_interface")
                else:
                    return redirect("payment_portal")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    context = {"form": form}
    return render(request, "login.html", context)


def logoutUser(request):
    logout(request)
    return redirect("home")


# ----------------PROPERTIES---------------
class PropertiesView(TemplateView):
    template_name = "properties.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["properties"] = RentalProperty.objects.all()
        context["property_images"] = PropertyPhoto.objects.all()
        # print(context["property_images"].values())
        return context


class CreatePropertyView(CreateView):
    model = RentalProperty
    form_class = UpdatePropertyForm
    template_name = "update_property.html"
    success_url = reverse_lazy("")

    def post(self, request):
        RentalProperty.objects.update()


class UpdatePropertyView(UpdateView):
    model = RentalProperty
    form_class = UpdatePropertyForm
    template_name = "update_property.html"
    success_url = reverse_lazy("")

    def post(self, request):
        RentalProperty.objects.update()


# --------------------TENANTS/USERS----------------
@method_decorator(login_required, name="dispatch")
class UserProfileDetailView(View):
    template_name = "user_profile_detail.html"

    def get(self, request, *args, **kwargs):
        tenant = request.user.tenant
        tenant_form = TenantForm(instance=tenant)
        context = {
            "tenant_form": tenant_form,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        tenant = request.user.tenant
        tenant_form = TenantForm(request.POST, request.FILES, instance=tenant)

        if tenant_form.is_valid():
            tenant_form.save()

        context = {
            "tenant_form": tenant_form,
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name="dispatch")
@method_decorator(staff_member_required, name="dispatch")
class ManagerInterfaceView(TemplateView):
    template_name = "manager.html"

    # COULD DO THIS BUT WE'LL SEE
    # # Calculate the starting index for the next set of records (in this case, 5).
    # next_starting_index = 5

    # # Fetch the next 5 records using slicing with the offset.
    # next_five_tenants = Tenant.objects.all()[next_starting_index: next_starting_index + 5]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["latest_tenants"] = Tenant.objects.all()
        context["properties"] = RentalProperty.objects.all()
        context["tenants"] = Tenant.objects.filter(linkToProperty__isnull=False)
        return context


##-----------landing pages------------##


class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["latest_properties"] = RentalProperty.objects.all()[:5]
        return context


def PaymentPortal(request):
    context = {}
    return render(request, "payment_portal.html", context)


def contractView(request):
    context = {}
    return render(request, "contract.html", context)


def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            email = form.cleaned_data["email"]
            phone = form.cleaned_data["phone"]
            subject = form.cleaned_data["subject"]
            message = form.cleaned_data["message"]

            try:
                # Customize your email settings below
                send_mail(
                    subject,
                    f"Name: {first_name} {last_name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}",
                    email,
                    [""],
                    fail_silently=False,
                )
                print("BOOOO")  # This is just for debugging purposes
            except smtplib.SMTPException as e:
                # Handle the exception or display an error message to the user
                print(f"Error sending email: {e}")
                # You can also add a message to the user using Django's messages framework.
                # Example: messages.error(request, "Error sending email. Please try again later.")
            return redirect("contact.html")
    else:
        form = ContactForm()

    return render(request, "contact.html", {"form": form})
