from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from django.views.generic import (
    TemplateView,
    UpdateView,
    DetailView,
    CreateView,
    DeleteView,
)
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
from django.conf import settings
import smtplib

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
# class PropertiesView(TemplateView):
#     template_name = "properties.html"
#     # Number of items per page

#     def get_context_data(self, **kwargs):
#         paginate_by = 10
#         context = super().get_context_data(**kwargs)

#         # Retrieve all rental properties and property photos
#         all_properties = RentalProperty.objects.all()
#         all_property_photos = PropertyPhoto.objects.all()

#         # Create a Paginator instance
#         paginator = Paginator(all_properties, paginate_by)

#         # Get the current page number from the request's GET parameters
#         page_number = self.request.GET.get("page")

#         try:
#             # Get the current page's RentalProperty queryset
#             properties = paginator.page(page_number)
#         except PageNotAnInteger:
#             # If page_number is not an integer, show the first page
#             properties = paginator.page(1)
#         except EmptyPage:
#             # If page_number is out of range (e.g., 9999), show the last page
#             properties = paginator.page(paginator.num_pages)

#         # Add the paginated queryset and property photos to the context
#         context["properties"] = properties
#         context["property_images"] = all_property_photos

#         return context


class PropertiesView(TemplateView):
    template_name = "properties.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        next_starting_index = 0

        # Check if the 'results' and 'search_query' keyword arguments are present
        if "results" in self.kwargs and "search_query" in self.kwargs:
            context["results"] = self.kwargs["results"]
            context["search_query"] = self.kwargs["search_query"]
        else:
            context["properties"] = RentalProperty.objects.all()[
                next_starting_index : next_starting_index + 12
            ]
            context["property_images"] = PropertyPhoto.objects.all()[
                next_starting_index : next_starting_index + 12
            ]

        return context


# @method_decorator(login_required, name="dispatch")
# @method_decorator(staff_member_required, name="dispatch")
class CreatePropertyView(CreateView):
    template_name = "create_property.html"
    success_url = "manager_interface"

    def get(self, request):
        property_form = CreatePropertyForm()
        property_photo = PropertyPhotoForm()
        context = {"property_form": property_form, "property_photo": property_photo}
        return render(request, self.template_name, context)

    def post(self, request):
        property_form = CreatePropertyForm(request.POST)
        property_photo = PropertyPhotoForm(request.POST)
        if property_form.is_valid():
            property_form.save()
            redirect("manager_interface")
        context = {"property_form": property_form, "property_photo": property_photo}

        return render(request, self.template_name, context)


# @method_decorator(login_required, name="dispatch")
# @method_decorator(staff_member_required, name="dispatch")
class UpdatePropertyView(UpdateView):
    template_name = "update_property.html"
    success_url = "manager_interface"

    def get(self, request, pk):
        property = RentalProperty.objects.get(id=pk)
        property_form = CreatePropertyForm(instance=property)
        context = {"property_form": property_form}
        return render(request, self.template_name, context)

    def post(self, request, pk):
        property = RentalProperty.objects.get(id=pk)
        property_form = CreatePropertyForm(request.POST, instance=property)

        if property_form.is_valid():
            property_form.save()

        context = {"property_form": property_form}

        return render(request, self.template_name, context)


# @method_decorator(login_required, name="dispatch")
# @method_decorator(staff_member_required, name="dispatch")
class PropertyDeleteView(View):
    def get(self, request, pk):
        property = get_object_or_404(RentalProperty, pk=pk)
        return render(request, "delete_property.html", {"property": property})

    def post(self, request, pk):
        property = get_object_or_404(RentalProperty, pk=pk)

        if "confirm" in request.POST:
            property.delete()
        return redirect("home")


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


# @method_decorator(login_required, name="dispatch")
# @method_decorator(staff_member_required, name="dispatch")
class ManagerInterfaceView(TemplateView):
    template_name = "manager.html"

    # COULD DO THIS BUT WE'LL SEE
    # # Calculate the starting index for the next set of records (in this case, 5).

    # # Fetch the next 5 records using slicing with the offset.
    # next_five_tenants = Tenant.objects.all()[next_starting_index: next_starting_index + 5]

    def get_context_data(self, **kwargs):
        next_starting_index = 0
        context = super().get_context_data(**kwargs)
        context["latest_tenants"] = Tenant.objects.all()[
            next_starting_index : next_starting_index + 10
        ]
        context["properties"] = RentalProperty.objects.all()[:10]
        context["tenants"] = Tenant.objects.filter(linkToProperty__isnull=False)
        return context


##-----------landing pages------------##


class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured_property"] = RentalProperty.objects.get(
            isFeaturedProperty=True
        )
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
            # if request.POST["choices"] == "rentals":

            first_name = request.POST["first_name"]
            last_name = request.POST["last_name"]
            email = request.POST["email"]
            phone = request.POST["phone"]
            subject = request.POST["subject"]
            message = request.POST["message"]

            # Send the email here
            try:
                send_mail(
                    subject,
                    f"Name: {first_name} {last_name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}",
                    email,
                    [
                        "bryanmcmurry7@gmail.com",
                    ],  # Replace with the actual recipient email address
                    fail_silently=False,
                )
                # Add success message or redirect to a success page
                return redirect("home")
            except Exception as e:
                # Handle the email sending error, add error message or redirect to an error page
                return redirect("manager_interface")
        else:
            print(form.errors)
    else:
        form = ContactForm()

    return render(request, "contact.html", {"form": form})


# class ProfileSearchView(ListView)
#     template_name = '/your/template.html'
#     model = Person

#     def get_queryset(self):
#         name = self.kwargs.get('name', '')
#         object_list = self.model.objects.all()
#         if name:
#             object_list = object_list.filter(name__icontains=name)
#         return object_list


def search_property(request):
    if request.method == "POST":
        form = PropertySearchForm(request.POST)
        if form.is_valid():
            search_field = form.cleaned_data["search_field"]
            search_query = form.cleaned_data["search_query"]

            # Create a dictionary to map form field names to model field names
            field_mapping = {
                "address": "address__icontains",
                "city": "city__icontains",
                "isRented": "isRented__icontains",
                "price": "price__icontains",
                "squareFoot": "squarefoot__icontains",
                "numOfBedrooms": "numOfBedrooms__icontains",
                "numOfBathrooms": "numOfBathrooms__icontains",
                "isPetFriendly": "isPetFriendly__icontains",
            }

            if search_field in field_mapping:
                query_field = field_mapping[search_field]
                results = RentalProperty.objects.filter(**{query_field: search_query})
                return redirect(
                    "properties", results=results, search_query=search_query
                )

    else:
        form = PropertySearchForm()

    return render(request, "properties", {"form": form})
