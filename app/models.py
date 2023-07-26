from django.db import models
from django.contrib.auth.models import User


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
    pricePerMonth = models.FloatField(verbose_name="Price")
    squareFoot = models.IntegerField(verbose_name="Square Footage")
    numOfBedrooms = models.IntegerField(verbose_name="Bedrooms")
    numOfBathrooms = models.FloatField(verbose_name="Bathrooms")
    isPetFriendly = models.BooleanField(verbose_name="Pet Friendly")
    description = models.TextField()

    def __str__(self):
        return self.address


# Exists so a property can have multiple photos
class PropertyPhoto(models.Model):
    picture = models.ImageField(upload_to="images/")
    propertyOfImage = models.ForeignKey(
        "RentalProperty", on_delete=models.PROTECT, null=True, blank=True
    )


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
