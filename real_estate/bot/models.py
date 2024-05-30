from django.db import models


# Create your models here.
class UserInfo(models.Model):
    phone_number = models.CharField(max_length=15)
    name = models.CharField(max_length=50)
    CHOICES = [
        ('sell', 'Продати квартиру'),
        ('rent', 'Здати квартиру'),
    ]
    option = models.CharField(max_length=4, choices=CHOICES)
    price = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

