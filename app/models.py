from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.utils import timezone
from django.utils.text import slugify
import calendar
from .utils import *
from datetime import datetime, timedelta
from django.db.models.signals import pre_delete


class Tenant(models.Model):
    linkToBuiltinUser = models.OneToOneField(User, on_delete=models.PROTECT)
    slug = models.SlugField(unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    userEmail = models.EmailField(max_length=254, verbose_name="Email")
    dateCreated = models.DateTimeField(auto_now_add=True)
    linkToLease = models.ForeignKey(
        "Lease", on_delete=models.SET_NULL, blank=True, null=True
    )

    def save(self, *args, **kwargs):
        # if self.slug is None:
        #     self.slug = slugify(self.first_name + self.last_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.first_name + " " + self.last_name


@receiver(pre_save, sender=Tenant)
def tenant_pre_save(sender, instance, *args, **kwargs):
    if instance.slug is None:
        slugify_instance_tenant(instance, save=False)


@receiver(post_save, sender=Tenant)
def tenant_post_save(sender, instance, created, *args, **kwargs):
    if created:
        slugify_instance_tenant(instance, save=True)


class Lease(models.Model):
    slug = models.SlugField(blank=True, null=True)
    pricePerMonth = models.FloatField(default=0, verbose_name="Price")
    isLate = models.BooleanField(default=False, verbose_name="Rent is Late")
    lateFee = models.FloatField(default=0, verbose_name="Late Fee")
    startDate = models.DateField(verbose_name="Lease Start Date")
    dueDate = models.DateField(verbose_name="Rent Due Date")
    endDate = models.DateField(blank=True, null=True, verbose_name="Lease End Date")
    monthsLeft = models.IntegerField(
        default=0, verbose_name="Months Remaining on Lease"
    )
    currentBalance = models.FloatField(default=0, verbose_name="Balance")
    linkToProperty = models.OneToOneField(
        "RentalProperty",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Address",
    )

    def __str__(self):
        return f"{self.linkToProperty}"

    def save(self, *args, **kwargs):
        if self.startDate and self.endDate:
            today = datetime.now().date()
            difference = self.endDate - today
            self.monthsLeft = max(difference.days // 30, 0)
        if not self.pk:
            today = timezone.now().date()
            next_month = today.replace(day=1) + timezone.timedelta(days=32)
            next_due_day = min(
                5, calendar.monthrange(next_month.year, next_month.month)[1]
            )
            self.dueDate = next_month.replace(day=next_due_day)
        super(Lease, self).save(*args, **kwargs)


class RentalProperty(models.Model):
    LOCATIONS = (
        ("Oxford", "Oxford"),
        ("Tupelo", "Tupelo"),
        ("Saltillo", "Saltillo"),
        ("Baldwyn", "Baldwyn"),
        ("West Point", "West Point"),
        ("Booneville", "Booneville"),
        ("Guntown", "Guntown"),
        ("Amory", "Amory"),
        ("New Albany", "New Albany"),
    )
    slug = models.SlugField(blank=True, null=True)
    address = models.CharField(max_length=50)
    city = models.TextField(null=True, choices=LOCATIONS)
    isRented = models.BooleanField(default=False, verbose_name="Occupied")
    price = models.FloatField(verbose_name="Price")
    squareFoot = models.IntegerField(verbose_name="Square Footage")
    bedrooms = models.IntegerField(verbose_name="Bedrooms")
    bathrooms = models.FloatField(verbose_name="Bathrooms")
    isPetFriendly = models.BooleanField(verbose_name="Pet Friendly")
    isFeaturedProperty = models.BooleanField(default=False, verbose_name="Featured")
    description = models.TextField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return self.address


# Exists so a property can have multiple photos
class PropertyPhoto(models.Model):
    picture = models.ImageField(upload_to="images/")
    propertyOfImage = models.ForeignKey(
        "RentalProperty", on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return f"{self.propertyOfImage}"


class ConstructionJob(models.Model):
    slug = models.SlugField(blank=True, null=True)
    title = models.CharField(max_length=50)
    isFeaturedConstruction = models.BooleanField(
        default=False, verbose_name="Featured Construction"
    )
    dateCreated = models.DateField(auto_now_add=True)
    isComplete = models.BooleanField(default=False)
    description = models.TextField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ConstructionJobPhoto(models.Model):
    picture = models.ImageField(upload_to="images/")
    constructionOfImage = models.ForeignKey(
        "ConstructionJob", on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return f"{self.constructionOfImage}"


class TenantPayment(models.Model):
    app_user = models.ForeignKey("Tenant", on_delete=models.CASCADE)
    payment_bool = models.BooleanField(default=False)
    stripe_checkout_id = models.CharField(max_length=500)
    payment_amount = models.FloatField(default=0)
    dateCreated = models.DateField(auto_now_add=True)
    dueDate = models.DateField(null=True, blank=True)
    linked_lease = models.ForeignKey(
        "Lease", on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"{self.app_user}: {self.payment_amount} @ {self.dateCreated}"


@receiver(post_save, sender=Tenant)
def create_user_payment(sender, instance, created, **kwargs):
    if created:
        lease = instance.linkToLease
        if lease:
            TenantPayment.objects.create(
                app_user=instance,
                linked_lease=lease,
                dueDate=lease.dueDate,
            )
        else:
            TenantPayment.objects.create(app_user=instance)
