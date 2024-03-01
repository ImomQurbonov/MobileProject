import datetime
import hashlib
from time import timezone

from django.db import models
from django.utils import timezone

from django.utils.text import slugify
from os.path import splitext

from mptt.models import MPTTModel

from accounts.views import User


def slugify_upload(instance, filename):
    folder = instance._meta.model_name
    name, ext = splitext(filename)
    name_t = slugify(name) or name
    return f"{folder}/{name_t}{ext}"


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    rate = models.IntegerField(default=0)
    sold_quantity = models.IntegerField(default=0)
    quantity = models.IntegerField(default=0)
    price = models.FloatField()
    category = models.ForeignKey('main.Category', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return self.name


class ProductSizeColor(models.Model):
    size = models.ForeignKey('main.Size', on_delete=models.CASCADE, blank=True, null=True)
    color = models.ForeignKey('main.Color', on_delete=models.CASCADE, blank=True, null=True)
    product = models.ForeignKey('main.Product', on_delete=models.CASCADE, blank=True, null=True)


class Category(models.Model):
    name = models.CharField(max_length=100)
    count_product = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class Size(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class CategoryFile(models.Model):
    category_file = models.FileField(upload_to=slugify_upload, blank=True, null=True)
    category_hash = models.CharField(max_length=160, blank=True, null=True)
    category_id = models.ForeignKey('main.Category', on_delete=models.CASCADE, blank=True, null=True)
    uploaded_at = models.DateTimeField(default=datetime.datetime.utcnow)

    def save(self, *args, **kwargs):
        input = self.category_file.name
        result = hashlib.sha256(input.encode())
        self.hash = result.hexdigest()
        super(CategoryFile, self).save(*args, **kwargs)

    def __str__(self):
        return self.category_file.name


class File(models.Model):
    file = models.FileField(upload_to=slugify_upload, blank=True, null=True)
    hash = models.CharField(max_length=150, blank=True, null=True, unique=True)
    product = models.ForeignKey('main.Product', on_delete=models.CASCADE, blank=True, null=True)
    uploaded_at = models.DateTimeField(default=datetime.datetime.utcnow)

    def save(self, *args, **kwargs):
        input = self.file.name
        result = hashlib.sha256(input.encode())
        self.hash = result.hexdigest()
        super(File, self).save(*args, **kwargs)

    def __str__(self):
        return self.file.name


class ShoppingCart(models.Model):
    product_id = models.ForeignKey('main.Product', on_delete=models.CASCADE)
    count_product = models.IntegerField(default=1)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=datetime.datetime.now)


class PromoCode(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    max_usage = models.PositiveIntegerField(default=1)
    current_usage = models.PositiveIntegerField(default=0)

    def is_valid(self):
        return self.start_date <= timezone.now() <= self.end_date and self.current_usage < self.max_usage

    def use(self):
        if self.is_valid():
            self.current_usage += 1
            self.save()

    def __str__(self):
        return self.code


class Order(models.Model):
    STATUS_CHOICES = (
        ('processing', 'Processing'),
        ('completed', 'Completed')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    shipping_address = models.ForeignKey('customer.ShippingAddress', on_delete=models.CASCADE, blank=True, null=True)
    product = models.ForeignKey('main.Product', on_delete=models.CASCADE, blank=True, null=True)
    count_product = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    created_at = models.DateTimeField(default=timezone.now)


class UserWallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    cash = models.FloatField(default=10000)
    created_at = models.DateTimeField(default=datetime.datetime.now)


class ReviewModel(models.Model):
    user_id = models.ForeignKey('auth.User', on_delete=models.CASCADE, blank=True, null=True)
    product_id = models.ForeignKey('main.Product', on_delete=models.CASCADE, blank=True, null=True)
    comment = models.TextField()
    star = models.FloatField()
    reviewed_at = models.DateTimeField(default=datetime.datetime.utcnow)


class LikeModel(models.Model):
    user_id = models.ForeignKey('auth.User', on_delete=models.CASCADE, blank=True, null=True)
    product_id = models.ForeignKey('main.Product', on_delete=models.CASCADE, blank=True, null=True)
    like = models.IntegerField()
    reviewed_at = models.DateTimeField(default=datetime.datetime.utcnow)
