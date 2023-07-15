from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Profile(models.Model):
    person = models.OneToOneField(User, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    userEmail = models.EmailField(max_length=254)
    currentBalance = models.IntegerField(default=0)
    dateCreated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.firstname + self.lastname
