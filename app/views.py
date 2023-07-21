from django.shortcuts import render, redirect
from django.forms import inlineformset_factory
from django.views.generic.base import TemplateView, DetailView, UpdateView
from django.utils.decorators import method_decorator

from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from .forms import *
from .models import *
from .decorators import *

from django.contrib.auth.models import Group
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required


class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["latest_properties"] = RentalProperty.objects.all()[:5]
        return context


# def homeView(request):
#     context = {}
#     return render(request, "home2.html", context)


@method_decorator(login_required, name="dispatch")
class UserProfileDetailView(DetailView):
    model = Tenant
    template_name = "user_profile_detail.html"
    context_object_name = "user_profile"


@method_decorator(login_required, name="dispatch")
class UserProfileUpdateView(UpdateView):
    model = Tenant
    fields = [
        "first_name",
        "last_name",
        "phone",
        "userEmail",
    ]
    template_name = "user_profile_update.html"


def rentView(request):
    context = {}
    return render(request, "payRent.html", context)


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
            user.first_name = form.cleaned_data.get(
                "first_name"
            )  # Access first name from the form data
            user.last_name = form.cleaned_data.get(
                "last_name"
            )  # Access last name from the form data
            user.save()  # Save the user with updated first name and last name

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
                context = {"form": form, "error_messages": error_messages}

    context = {"form": form}
    return render(request, "register.html", context)


@unauthenticated_user
def loginPage(request):
    form = AuthenticationForm()

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(request, username=username, password=password)

            if user is not None:
                messages.success(request, "Welcome" + username)
                login(request, user)
                return redirect("rent")

            else:
                messages.info(request, "Username OR Password is Incorrect")

    context = {"form": form}
    return render(request, "login.html", context)


def logoutUser(request):
    logout(request)
    return redirect("home")
