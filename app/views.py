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
from django.http import JsonResponse
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
        category = self.request.GET.get("category")
        sort_order = self.request.GET.get("sort")

        if category and sort_order:
            property_images = PropertyPhoto.objects.all()
            if sort_order == "asc":
                properties = properties.order_by(f"{category}")
            elif sort_order == "desc":
                properties = properties.order_by(f"-{category}")

        # Pagination
        page_number = self.request.GET.get("page")
        p = Paginator(properties, self.ITEMS_PER_PAGE)
        p_images = Paginator(property_images, self.ITEMS_PER_PAGE)

        context["properties"] = p.get_page(page_number)
        context["property_photo"] = p_images.get_page(page_number)

        return context


@method_decorator(login_required, name="dispatch")
@method_decorator(staff_member_required, name="dispatch")
class CreatePropertyView(View):
    template_name = "create_property.html"

    def get(self, request, *args, **kwargs):
        PropertyPhotoFormSet = formset_factory(PropertyPhotoForm, extra=5)
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
        property_form = UpdatePropertyForm(request.POST, instance=property)
        photos = PropertyPhoto.objects.filter(propertyOfImage=property)
        property_photo_form = PropertyPhotoForm(request.POST, request.FILES)

        if property_form.is_valid() and property_photo_form.is_valid():
            property = property_form.save(commit=False)
            property.pk = pk
            property.save()
            property_photo = property_photo_form.save(commit=False)
            property_photo.propertyOfImage = property
            if property_photo.picture != "":
                property_photo.save()

            return redirect("manager_interface")
        else:
            print(property_form.errors)
            print(property_photo_form.errors)
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


@method_decorator(login_required, name="dispatch")
@method_decorator(staff_member_required, name="dispatch")
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


@method_decorator(login_required, name="dispatch")
@method_decorator(staff_member_required, name="dispatch")
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


# --------------------LEASE----------------
@method_decorator(login_required, name="dispatch")
@method_decorator(staff_member_required, name="dispatch")
class CreateLeaseView(CreateView):
    template_name = "create_lease.html"
    form_class = LeaseForm
    success_url = reverse_lazy("manager_interface")

    def form_valid(self, form):
        lease = form.save()
        selected_tenants = form.cleaned_data["selected_tenant"]

        # Loop through the selected tenants and link each one to the lease
        for tenant in selected_tenants:
            tenant.linkToLease = lease
            tenant.save()

        return super().form_valid(form)


@method_decorator(login_required, name="dispatch")
@method_decorator(staff_member_required, name="dispatch")
class UpdateLeaseView(UpdateView):
    template_name = "update_lease.html"
    success_url = reverse_lazy("manager_interface")

    def get(self, request, pk):
        lease = Lease.objects.get(id=pk)
        lease_form = LeaseForm(instance=lease)

        context = {
            "lease_form": lease_form,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        lease = Lease.objects.get(id=pk)
        lease_form = LeaseForm(request.POST, instance=lease)

        if lease_form.is_valid():
            lease_form.save()

            return redirect("manager_interface")
        context = {
            "lease_form": lease_form,
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name="dispatch")
@method_decorator(staff_member_required, name="dispatch")
class LeaseDeleteView(View):
    def get(self, request, pk):
        lease = get_object_or_404(Lease, pk=pk)
        tenants = Tenant.objects.filter(linkToLease=lease)
        return render(
            request, "delete_lease.html", {"lease": lease, "tenants": tenants}
        )

    def post(self, request, pk):
        lease = get_object_or_404(Lease, pk=pk)
        tenants = Tenant.objects.filter(linkToLease=lease)
        if "confirm" in request.POST:
            lease.delete()
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
        context["construction"] = ConstructionJob.objects.all()
        context["tenants"] = Tenant.objects.filter(linkToLease__isnull=False)

        for lease in context["leases"]:
            balance = lease.currentBalance
            lease.monthsLeft = (lease.endDate - lease.startDate).days // 30
            if lease.dueDate < timezone.now().date() and balance < 0:
                lease.isLate = True
                late_fee = 20  # Example late fee amount
                lease.lateFee += late_fee
                balance -= late_fee
            else:
                lease.isLate = False
                lease.lateFee = 0  # Reset late fee if not late

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
        featured_construction = ConstructionJob.objects.filter(
            isFeaturedConstruction=True
        ).first()
        if featured_construction:
            context["featured_construction"] = featured_construction
            context["construction_photo"] = ConstructionJobPhoto.objects.filter(
                constructionOfImage=featured_construction
            ).first()
        return context


# ----------------CONSTRUCTION---------------
class ConstructionView(TemplateView):
    template_name = "construction.html"
    ITEMS_PER_PAGE = 12

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        construction_jobs = ConstructionJob.objects.all()
        construction_images = ConstructionJobPhoto.objects.all()

        # SEARCH BAR
        search_query = self.request.GET.get("search")
        if search_query:
            construction_jobs = construction_jobs.filter(
                Q(title__icontains=search_query)
                | Q(description__icontains=search_query)
            )
            construction_images = construction_images.filter(
                constructionOfImage__in=construction_jobs
            )

        # SORT BY
        category = self.request.GET.get("category")
        sort_order = self.request.GET.get("sort")

        if category and sort_order:
            construction_images = ConstructionJobPhoto.objects.all()
            if sort_order == "asc":
                construction_jobs = construction_jobs.order_by(f"{category}")
            elif sort_order == "desc":
                construction_jobs = construction_jobs.order_by(f"-{category}")

        # Pagination
        page_number = self.request.GET.get("page")
        p = Paginator(construction_jobs, self.ITEMS_PER_PAGE)
        p_images = Paginator(construction_images, self.ITEMS_PER_PAGE)

        context["construction_jobs"] = p.get_page(page_number)
        context["construction_images"] = p_images.get_page(page_number)

        return context


@method_decorator(login_required, name="dispatch")
@method_decorator(staff_member_required, name="dispatch")
class CreateConstructionView(View):
    template_name = "create_construction.html"

    def get(self, request, *args, **kwargs):
        ConstructionPhotoFormSet = formset_factory(ConstructionPhotoForm, extra=5)
        construction_form = CreateConstructionForm()
        construction_photo_formset = ConstructionPhotoFormSet()

        context = {
            "construction_form": construction_form,
            "construction_photo_formset": construction_photo_formset,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        ConstructionPhotoFormSet = formset_factory(ConstructionPhotoForm, extra=1)

        construction_form = CreateConstructionForm(request.POST)
        construction_photo_formset = ConstructionPhotoFormSet(
            request.POST, request.FILES
        )

        if construction_form.is_valid() and construction_photo_formset.is_valid():
            construction_job = construction_form.save()

            for form in construction_photo_formset:
                if form.is_valid() and form.cleaned_data.get("picture"):
                    construction_photo_instance = form.save(commit=False)
                    construction_photo_instance.constructionOfImage = construction_job
                    construction_photo_instance.save()

            return redirect("manager_interface")

        context = {
            "construction_form": construction_form,
            "construction_photo_formset": construction_photo_formset,
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name="dispatch")
@method_decorator(staff_member_required, name="dispatch")
class UpdateConstructionView(UpdateView):
    template_name = "update_construction.html"
    success_url = "manager_interface"

    def get(self, request, pk):
        construction = ConstructionJob.objects.get(id=pk)
        construction_form = CreateConstructionForm(instance=construction)
        photos = ConstructionJobPhoto.objects.filter(constructionOfImage=construction)

        # Get existing photos associated with the RentalProperty
        construction_photo_form = ConstructionPhotoForm()

        context = {
            "construction_form": construction_form,
            "construction_photo_form": construction_photo_form,
            "photos": photos,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        construction = ConstructionJob.objects.get(id=pk)
        construction_form = CreateConstructionForm(request.POST, instance=construction)
        photos = ConstructionJobPhoto.objects.filter(constructionOfImage=construction)
        construction_photo_form = PropertyPhotoForm(request.POST, request.FILES)

        if construction_form.is_valid() and construction_photo_form.is_valid():
            construction_form.save()

            construction_photo = construction_photo_form.save(commit=False)
            construction_photo.constructionOfImage = construction
            if construction_photo.picture != "":
                construction_photo.save()

            return redirect("manager_interface")
        context = {
            "construction_form": construction_form,
            "construction_photo_form": construction_photo_form,
            "photos": photos,
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name="dispatch")
@method_decorator(staff_member_required, name="dispatch")
class ConstructionDeleteView(View):
    def get(self, request, pk):
        construction = get_object_or_404(ConstructionJob, pk=pk)
        return render(
            request, "delete_construction.html", {"construction": construction}
        )

    def post(self, request, pk):
        construction = get_object_or_404(ConstructionJob, pk=pk)

        if "confirm" in request.POST:
            construction.delete()
        return redirect("manager_interface")


@method_decorator(login_required, name="dispatch")
@method_decorator(staff_member_required, name="dispatch")
class ConstructionPhotoDeleteView(View):
    def get(self, request, pk):
        photo = get_object_or_404(ConstructionJobPhoto, pk=pk)
        if "confirm" in request.POST:
            photo.delete()
        return render(request, "delete_construction_photo.html", {"photo": photo})

    def post(self, request, pk):
        photo = get_object_or_404(ConstructionJobPhoto, pk=pk)
        if "confirm" in request.POST:
            photo.delete()
        return redirect("manager_interface")


@method_decorator(login_required, name="dispatch")
@method_decorator(staff_member_required, name="dispatch")
class SetConstructionToFeaturedView(View):
    def get(self, request, pk):
        construction = get_object_or_404(ConstructionJob, pk=pk)
        return render(
            request, "feature_construction.html", {"construction": construction}
        )

    def post(self, request, pk):
        # Retrieve all rental properties
        if "confirm" in request.POST:
            all_construction_jobs = ConstructionJob.objects.all()

            # Set 'isFeaturedProperty' to False for all RentalProperty objects
            for each in all_construction_jobs:
                each.isFeaturedConstruction = False
                each.save()

            # Get the selected property and set its 'isFeaturedProperty' to True
            obj = get_object_or_404(ConstructionJob, pk=pk)
            obj.isFeaturedConstruction = True
            obj.save()

        return redirect("manager_interface")


# ----------------EMAIL---------------
def contact_view(request):
    if request.method == "POST":
        contact_view = ContactForm(request.POST)
        if contact_view.is_valid():
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
                return render(request, "home")
            except Exception as e:
                # Handle the email sending error, add error message or redirect to an error page
                return redirect("properties")
        else:
            print(contact_view.errors)
    else:
        contact_view = ContactForm()

    return render(request, "contact.html", {"contact_view": contact_view})


def quote_view(request):
    if request.method == "POST":
        form = QuoteForm(request.POST)
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
                return redirect("properties")
        else:
            print(form.errors)
    else:
        form = QuoteForm()

    return render(request, "construction.html", {"form": form})


##===============below is the payment views for stripe============================##
def PaymentPortal(request):
    user_id = request.user.id
    try:
        tenant = Tenant.objects.get(linkToBuiltinUser__id=user_id)
    except Tenant.DoesNotExist:
        tenant = None

    if tenant:
        payment_history = TenantPayment.objects.filter(app_user=tenant)
        lease = None
        if tenant.linkToLease:
            lease = Lease.objects.get(id=tenant.linkToLease.id)

        if lease:
            # Tenant has a lease
            print(lease)
        else:
            # Tenant does not have a lease
            properties = RentalProperty.objects.all()
            search_query = request.GET.get("search")
            if search_query:
                properties = properties.filter(
                    Q(address__icontains=search_query) | Q(city__icontains=search_query)
                )

            print(tenant)
            print(payment_history)

    stripe.api_key = settings.STRIPE_SECRET_KEY
    if request.method == "POST":
        payment_amount = float(request.POST.get("payment_amount"))
        # Create a product dynamically if not already created
        product = stripe.Product.create(
            name="Rent",
            description="A dynamically created product for custom payments",
        )

        # Create a Price object with dynamic price using line_items.price_data
        price = stripe.Price.create(
            unit_amount=int(payment_amount * 100),  # Convert to cents
            currency="usd",
            product=product.id,
        )
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price.id,
                    "quantity": 1,
                }
            ],
            mode="payment",
            customer_creation="always",
            success_url=settings.REDIRECT_DOMAIN
            + "payment_success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=settings.REDIRECT_DOMAIN + "payment_fail",
        )
        return redirect(checkout_session.url, code=303)
    return render(request, "payment_portal.html")


def PaymentSuccess(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    checkout_session_id = request.GET.get("session_id", None)
    session = stripe.checkout.Session.retrieve(checkout_session_id)

    customer = stripe.Customer.retrieve(session.customer)
    user = request.user  # Fix: Removed duplicated line

    # Retrieve the logged-in tenant
    logged_in_tenant = Tenant.objects.get(linkToBuiltinUser=user)

    custom_amount = None
    for line_item in session.line_items.data:
        if line_item.price:
            custom_amount = (
                float(line_item.price.unit_amount) / 100
            )  # Convert from cents
            break  # Assuming you only need the first item, otherwise adjust accordingly

    if custom_amount is not None:
        lease = logged_in_tenant.linkToLease

        if lease:
            user_payment, created = TenantPayment.objects.get_or_create(
                app_user=logged_in_tenant
            )
            user_payment.payment_bool = True
            user_payment.payment_amount = custom_amount
            user_payment.linked_lease = lease
            user_payment.stripe_checkout_id = checkout_session_id
            user_payment.save()

            lease.currentBalance += custom_amount
            lease.save()

    return render(request, "payment_success.html", {"customer": customer})


def PaymentFail(request):
    return render(request, "payment_fail.html")


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
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

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        session_id = session.get("id", None)
        user_payment = TenantPayment.objects.get(stripe_checkout_id=session_id)
        user_payment.payment_bool = True
        user_payment.save()

    return HttpResponse(status=200)
