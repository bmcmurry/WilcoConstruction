from django.shortcuts import render, redirect
from django.forms import modelformset_factory, formset_factory
from django.views.generic import (
    TemplateView,
    UpdateView,
    DetailView,
    CreateView,
    DeleteView,
    View,
)
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.conf import settings
import smtplib
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import stripe
import time
import pdb
from django.views.decorators.csrf import csrf_exempt

from .forms import *
from .models import *
from .decorators import *
from django.db.models import Q

# Your code implementation goes here...


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


class PropertyView(TemplateView):
    template_name = "properties.html"
    ITEMS_PER_PAGE = 12

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        properties = RentalProperty.objects.all()
        property_images = PropertyPhoto.objects.all()

        # SEARCH BAR
        search_query = self.request.GET.get("search")
        if search_query:
            properties = properties.filter(
                Q(address__icontains=search_query)
                | Q(city__icontains=search_query)
                | Q(description__icontains=search_query)
            )
            property_images = property_images.filter(propertyOfImage__in=properties)

        # SORT BY
        sort_order = self.request.GET.get("sort")
        if sort_order == "asc":
            properties = properties.order_by("price")
        elif sort_order == "desc":
            properties = properties.order_by("-price")

        # Pagination
        page_number = self.request.GET.get("page")
        p = Paginator(properties, self.ITEMS_PER_PAGE)
        p_images = Paginator(property_images, self.ITEMS_PER_PAGE)

        context["properties"] = p.get_page(page_number)
        context["property_photo"] = p_images.get_page(page_number)

        return context


# @method_decorator(login_required, name="dispatch")
# @method_decorator(staff_member_required, name="dispatch")
class CreatePropertyView(View):
    template_name = "create_property.html"

    @method_decorator(login_required)
    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        PropertyPhotoFormSet = formset_factory(PropertyPhotoForm, extra=1)
        property_form = CreatePropertyForm()
        property_photo_formset = PropertyPhotoFormSet()

        context = {
            "property_form": property_form,
            "property_photo_formset": property_photo_formset,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        PropertyPhotoFormSet = formset_factory(PropertyPhotoForm, extra=1)

        property_form = CreatePropertyForm(request.POST)
        property_photo_formset = PropertyPhotoFormSet(request.POST, request.FILES)

        if property_form.is_valid() and property_photo_formset.is_valid():
            rental_property = property_form.save()

            for form in property_photo_formset:
                if form.is_valid() and form.cleaned_data.get("picture"):
                    property_photo_instance = form.save(commit=False)
                    property_photo_instance.propertyOfImage = rental_property
                    property_photo_instance.save()

            return redirect("manager_interface")

        context = {
            "property_form": property_form,
            "property_photo_formset": property_photo_formset,
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name="dispatch")
@method_decorator(staff_member_required, name="dispatch")
class UpdatePropertyView(UpdateView):
    template_name = "update_property.html"
    success_url = "manager_interface"

    def get(self, request, pk):
        property = RentalProperty.objects.get(id=pk)
        property_form = CreatePropertyForm(instance=property)
        photos = PropertyPhoto.objects.filter(propertyOfImage=property)

        # Get existing photos associated with the RentalProperty
        property_photo_form = PropertyPhotoForm()

        context = {
            "property_form": property_form,
            "property_photo_form": property_photo_form,
            "photos": photos,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        property = RentalProperty.objects.get(id=pk)
        property_form = CreatePropertyForm(request.POST, instance=property)

        photos = PropertyPhoto.objects.filter(propertyOfImage=property)
        property_photo_form = PropertyPhotoForm(
            request.POST,
            request.FILES,
        )

        if property_form.is_valid() and property_photo_form.is_valid():
            property_form.save()

            property_photo = property_photo_form.save(commit=False)
            property_photo.propertyOfImage = property
            if property_photo.picture != "":
                property_photo.save()

            return redirect("manager_interface")
        context = {
            "property_form": property_form,
            "property_photo_form": property_photo_form,
            "photos": photos,
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name="dispatch")
@method_decorator(staff_member_required, name="dispatch")
class PropertyDeleteView(View):
    def get(self, request, pk):
        property = get_object_or_404(RentalProperty, pk=pk)
        return render(request, "delete_property.html", {"property": property})

    def post(self, request, pk):
        property = get_object_or_404(RentalProperty, pk=pk)

        if "confirm" in request.POST:
            property.delete()
        return redirect("manager_interface")


class PhotoDeleteView(View):
    def get(self, request, pk):
        photo = get_object_or_404(PropertyPhoto, pk=pk)
        if "confirm" in request.POST:
            photo.delete()
        return render(request, "delete_photo.html", {"photo": photo})

    def post(self, request, pk):
        photo = get_object_or_404(PropertyPhoto, pk=pk)
        if "confirm" in request.POST:
            photo.delete()
        return redirect("manager_interface")


class SetPropertyToFeaturedView(View):
    def get(self, request, pk):
        property = get_object_or_404(RentalProperty, pk=pk)
        return render(request, "feature_property.html", {"property": property})

    def post(self, request, pk):
        # Retrieve all rental properties
        if "confirm" in request.POST:
            all_properties = RentalProperty.objects.all()

            # Set 'isFeaturedProperty' to False for all RentalProperty objects
            for each in all_properties:
                each.isFeaturedProperty = False
                each.save()

            # Get the selected property and set its 'isFeaturedProperty' to True
            obj = get_object_or_404(RentalProperty, pk=pk)
            obj.isFeaturedProperty = True
            obj.save()

        return redirect("manager_interface")


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["leases"] = Lease.objects.all()
        context["latest_tenants"] = Tenant.objects.all()
        context["properties"] = RentalProperty.objects.all()
        context["tenants"] = Tenant.objects.filter(linkToLease__isnull=False)
        return context


##-----------landing pages------------##


class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        featured_property = RentalProperty.objects.filter(
            isFeaturedProperty=True
        ).first()
        if featured_property:
            context["featured_property"] = featured_property
            context["property_photo"] = PropertyPhoto.objects.filter(
                propertyOfImage=featured_property
            ).first()
        # context["latest_properties"] = RentalProperty.objects.all()[:5]
        return context


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
            subject = request.POST["categories"]
            message = request.POST["message"]

            # Send the email here
            try:
                send_mail(
                    subject,
                    f"Name: {first_name} {last_name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}",
                    email,
                    [
                        settings.EMAIL_HOST_USER,
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


# def search_property(request):
#     if request.method == "POST":
#         form = PropertySearchForm(request.POST)
#         if form.is_valid():
#             search_field = form.cleaned_data["search_field"]
#             search_query = form.cleaned_data["search_query"]

#             # Create a dictionary to map form field names to model field names
#             field_mapping = {
#                 "address": "address__icontains",
#                 "city": "city__icontains",
#                 "isRented": "isRented__icontains",
#                 "price": "price__icontains",
#                 "squareFoot": "squarefoot__icontains",
#                 "bedrooms": "bedrooms__icontains",
#                 "bathrooms": "bathrooms__icontains",
#                 "isPetFriendly": "isPetFriendly__icontains",
#             }

#             if search_field in field_mapping:
#                 query_field = field_mapping[search_field]
#                 results = RentalProperty.objects.filter(**{query_field: search_query})
#                 return redirect(
#                     "properties", results=results, search_query=search_query
#                 )

#     else:
#         form = PropertySearchForm()

#     return render(request, "properties", {"form": form})


##===============below is the payment views for stripe============================##
def PaymentPortal(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if request.method == "POST":
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": settings.PRODUCT_PRICE,
                    "quantity": 1,
                },
            ],
            mode="payment",
            customer_creation="always",
            success_url=settings.REDIRECT_DOMAIN
            + "/payment_success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=settings.REDIRECT_DOMAIN + "/payment_fail",
        )
        return redirect(checkout_session.url, code=303)

    return render(request, "payment_portal.html")


def paymentSuccess(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    checkout_session_id = request.GET.get("session_id", None)
    session = stripe.checkout.Session.retrieve(checkout_session_id)
    customer = stripe.Customer.retrieve(session.customer)
    user_id = request.user.user_id
    user_payment = TenantPayment.objects.get(Tenant=user_id)
    user_payment.stripe_checkout_id = checkout_session_id
    user_payment.save()

    return render(request, "payment_success.html", {"customer": customer})


def paymentFail(request):
    return render(request, "payment_fail.html")


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    time.sleep(10)
    payload = request.body
    signature_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, signature_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)
    if event["type"] == "checkout.session.,completed":
        session = event["data"]["object"]
        session_id = session.get("id", None)
        time.sleep(15)
        user_payment = TenantPayment.objects.get(stripe_checkout_id=session_id)
        line_items = stripe.checkout.Session.list_line_items(session_id, limit=1)
        user_payment.payment_bool = True
        user_payment.save()
    return HttpResponse(status=200)
