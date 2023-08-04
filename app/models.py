from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save


# Create your models here.
class Tenant(models.Model):
    linkToBuiltinUser = models.OneToOneField(User, on_delete=models.PROTECT)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    userEmail = models.EmailField(max_length=254, verbose_name="Email")
    currentBalance = models.IntegerField(default=0, verbose_name="Balance")
    dateCreated = models.DateTimeField(auto_now_add=True)
    linkToProperty = models.ForeignKey(
        "RentalProperty", on_delete=models.CASCADE, blank=True, null=True
    )

    def __str__(self):
        return self.first_name + " " + self.last_name


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


class ConstructionTicket(models.Model):
    title = models.CharField(max_length=50)
    dateCreated = models.DateField(auto_now_add=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class ConstructionTicketPhoto(models.Model):
    picture = models.ImageField(upload_to="images/")
    ConstructionOfImage = models.ForeignKey(
        "ConstructionTicket", on_delete=models.PROTECT, null=True, blank=True
    )


class TenantPayment(models.Model):
    app_user = models.ForeignKey("Tenant", on_delete=models.CASCADE)
    payment_bool = models.BooleanField(default=False)
    stripe_checkout_id = models.CharField(max_length=500)


@receiver(post_save, sender=Tenant)
def create_user_payment(sender, instance, created, **kwargs):
    if created:
        TenantPayment.objects.create(app_user=instance)
