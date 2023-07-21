from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Tenant(models.Model):
    linkToBuiltinUser = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    userEmail = models.EmailField(max_length=254)
    currentBalance = models.IntegerField(default=0)
    dateCreated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.first_name + " " + self.last_name


class RentalProperty(models.Model):
    linkToTenant = models.OneToOneField("Tenant", on_delete=models.PROTECT, null=True)
    address = models.CharField(max_length=50)
    city = models.TextField
    isRented = models.BooleanField(default=False)
    pricePerMonth = models.FloatField()
    squareFoot = models.IntegerField()
    numOfBedrooms = models.IntegerField()
    numOfBathrooms = models.FloatField()
    isPetFriendly = models.BooleanField()
    picture = models.ImageField(upload_to="images/")
    description = models.TextField()
