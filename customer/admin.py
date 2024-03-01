from django.contrib import admin
from customer.models import State, City, Country, ShippingAddress, DiscountProduct, Favorite

admin.site.register((State, City, Country, ShippingAddress, DiscountProduct, Favorite))
