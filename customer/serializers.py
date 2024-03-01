from rest_framework import serializers
from customer.models import DiscountProduct, DiscountCategory


class FavouriteSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()


class ShippingAddressSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    postal_code = serializers.CharField()
    street_address = serializers.CharField()
    house_number = serializers.CharField()
    city = serializers.CharField()
    state = serializers.CharField()
    country = serializers.CharField()


class DiscountCategorySerializer(serializers.Serializer):
    discount_percentage = serializers.FloatField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()


class DiscountCategoryListserializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountCategory
        fields = '__all__'


class DiscountProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountProduct
        fields = '__all__'
