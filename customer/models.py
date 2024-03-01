from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from main.models import Category

User = get_user_model()


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey("main.Product", on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)


class Country(models.Model):
    name = models.CharField(max_length=25)


class State(models.Model):
    state = models.CharField(max_length=20)
    country = models.ForeignKey("customer.Country", on_delete=models.CASCADE)


class City(models.Model):
    city = models.CharField(max_length=20)
    state = models.ForeignKey("customer.State", on_delete=models.CASCADE)


class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    postal_code = models.CharField(max_length=20)
    street_address = models.CharField(max_length=255)
    house_number = models.CharField(max_length=50)
    state = models.ForeignKey("customer.State", on_delete=models.CASCADE)
    city = models.ForeignKey("customer.City", on_delete=models.CASCADE)
    country = models.ForeignKey("customer.Country", on_delete=models.CASCADE)

    def __str__(self):
        return (f" {self.street_address},{self.phone_number},"
                f" {self.city}, {self.state},{self.house_number},"
                f" {self.postal_code}, {self.country}")


class DiscountProduct(models.Model):
    product = models.ForeignKey("main.Product", on_delete=models.CASCADE)
    discount_percentage = models.FloatField()
    rate = models.IntegerField(default=0)
    sold_quantity = models.IntegerField(default=0)
    discounted_price = models.FloatField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()


class DiscountCategory(models.Model):
    category = models.ForeignKey("main.Category", on_delete=models.CASCADE)
    discount_percentage = models.FloatField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    img = models.ForeignKey('main.File', on_delete=models.CASCADE, blank=True, null=True)
    count_product = models.IntegerField(default=0)
