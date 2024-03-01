from django.core.validators import MaxValueValidator
from rest_framework import serializers
from .models import Order, UserWallet
from .models import LikeModel
from .models import ReviewModel
from .models import Product, Size, Category, File, Color, ProductSizeColor, ShoppingCart, PromoCode


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = '__all__'


class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('file', 'product')


class ProductFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('hash',)


class AddCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = '__all__'


class CreateProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('name', 'description', 'price', 'category', 'quantity')


class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = '__all__'


class GetProductSizeColorSerializer(serializers.ModelSerializer):
    size = SizeSerializer()
    color = ColorSerializer()
    product = ProductListSerializer()

    class Meta:
        model = ProductSizeColor
        fields = '__all__'

    def create(self, validated_data):
        return File.objects.create(**validated_data)


class GetProductSizeSerializer(serializers.ModelSerializer):
    size = SizeSerializer()

    class Meta:
        model = ProductSizeColor
        fields = ('size',)


class GetSizeColorSerializer(serializers.ModelSerializer):
    color = ColorSerializer()

    class Meta:
        model = ProductSizeColor
        fields = ('color',)


class ProductAddSizeColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSizeColor
        fields = '__all__'


class AddToShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('product_id', 'count_product')


sort_by_choices = (
    ('New_Today', 'New_This_Week', 'Top_sellers')
)


class FilterQuerySerializer(serializers.Serializer):
    category_id = serializers.CharField(required=False)
    start_price = serializers.IntegerField(required=False)
    end_price = serializers.IntegerField(required=False)
    sort_by = serializers.ChoiceField(choices=sort_by_choices)
    rate = serializers.IntegerField(validators=[MaxValueValidator(5)])


class PromoCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = ('discount',)


class QuerySerializer(serializers.Serializer):
    query = serializers.CharField(max_length=255)


class CreateOrderSerializer(serializers.ModelSerializer):
    product = ProductListSerializer()

    class Meta:
        model = Order
        fields = ('product', 'status', 'count_product')


class GetOrderSerializer(serializers.ModelSerializer):
    product = ProductListSerializer()

    class Meta:
        model = Order
        fields = '__all__'


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('product',)


class PaymentSerializer(serializers.Serializer):
    cash = serializers.FloatField()


class UserWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWallet
        fields = ('cash', 'created_at')


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model: ReviewModel
        fields = ('comment', 'star',)


class ReviewSerializersRes(serializers.ModelSerializer):
    class Meta:
        model: ReviewModel
        fields = '__all__'


class LikeSerializersRes(serializers.ModelSerializer):
    class Meta:
        model: LikeModel
        fields = '__all__'


class TemporarilyPhotosSerializer(serializers.Serializer):
    file = serializers.FileField()
