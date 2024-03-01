from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from customer.models import (
    DiscountProduct, ShippingAddress,
    Country, State, City,
    Favorite, DiscountCategory
)

from customer.serializers import (
    ShippingAddressSerializer,
    FavouriteSerializer,
    DiscountProductListSerializer,
    DiscountCategoryListserializer
)

from main.models import Product
from main.serializers import ProductListSerializer


class MyFavouriteAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FavouriteSerializer

    def post(self, request):
        user_id = request.user.id
        product_id = request.data.get('product_id')

        if not user_id:
            return Response({'success': False, "error": "user_id is required"})

        if not product_id:
            return Response({'success': False, 'error': 'Input should be integer !'})

        try:
            Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({'success': False, 'error': 'Product not found !!!'})

        try:
            favorite = Favorite.objects.get(user_id=user_id, product_id=product_id)
            favorite.delete()
            return Response({'success': True, 'detail': 'Removed'})
        except Favorite.DoesNotExist:
            user_product = Favorite.objects.create(
                user_id=user_id,
                product_id=product_id
            )
            user_product.save()
            return Response({'success': True, 'detail': 'Added'})

    def get(self, request):
        user_id = request.user.id

        if not user_id:
            return Response({'success': False, "error": "user_id is required"})

        favorites = Favorite.objects.filter(user_id=user_id)

        if not favorites:
            return Response('My favourite empty !!!')
        product_ids = [favorite.product_id for favorite in favorites]
        products = Product.objects.filter(pk__in=product_ids)
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


class ShippingAddressAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ShippingAddressSerializer

    def post(self, request):
        phone_number = request.data.get('phone_number')
        postal_code = request.data.get('postal_code')
        street_address = request.data.get('street_address')
        house_number = request.data.get('house_number')
        state_name = request.data.get('state')
        city_name = request.data.get('city')
        country_name = request.data.get('country')
        user = request.user.id

        if not user:
            return Response({'success': False, "error": "user_id is required"})
        if not country_name:
            return Response({'message': "Country name cannot be empty"})

        if phone_number is None or postal_code is None or street_address is None or house_number is None or state_name is None or city_name is None or country_name is None:
            return Response({'success': False, 'error': 'there is empty data.'})

        try:
            country = Country.objects.get(name=country_name)
        except Country.DoesNotExist:
            return Response({'success': False, 'detail': 'such a country does not exist !!!'})

        try:
            state = State.objects.get(state=state_name, country=country)
        except State.DoesNotExist:
            return Response({'success': False, 'detail': 'There is no state in such a country !!!'})

        try:
            city = City.objects.get(city=city_name, state=state.id)
            add_data = ShippingAddress.objects.create(
                user_id=request.user.id,
                phone_number=phone_number,
                postal_code=postal_code,
                street_address=street_address,
                house_number=house_number,
                country_id=country.id,
                state_id=state.id,
                city_id=city.id
            )
            return Response({'success': True, 'detail': 'Added'})
        except City.DoesNotExist:
            return Response({'success': False, 'detail': 'There is no city in such a state !!!'})

    def get(self, request):
        user_id = request.user.id

        if not user_id:
            return Response({'success': False, "error": "user_id is required"})

        data = []
        shipping_addresses = ShippingAddress.objects.filter(user_id=user_id)
        for addresses in shipping_addresses:
            country = Country.objects.get(pk=addresses.country.id)
            state = State.objects.get(pk=addresses.state.id)
            city = City.objects.get(pk=addresses.city.id)
            data.append({
                'phone_number': addresses.phone_number,
                'postal_code': addresses.postal_code,
                'street_address': addresses.street_address,
                'house_number': addresses.house_number,
                'city': city.city,
                'state': state.state,
                'country': country.name
            }
            )
        serializer = ShippingAddressSerializer(data, many=True)
        return Response(serializer.data)


class ShippingAddressUpdateAPIView(GenericAPIView):
    serializer_class = ShippingAddressSerializer

    def put(self, request, shipping_address_id):
        phone_number = request.data.get('phone_number')
        postal_code = request.data.get('postal_code')
        street_address = request.data.get('street_address')
        house_number = request.data.get('house_number')
        state_name = request.data.get('state')
        city_name = request.data.get('city')
        country_name = request.data.get('country')
        user = request.user.id

        if not user:
            return Response({'success': False, "error": "user_id is required"})

        try:
            title = ShippingAddress.objects.get(
                user_id=request.user.id,
                pk=shipping_address_id
            )
        except ObjectDoesNotExist:
            return Response({"error": "ShippingAddress not found"})

        try:
            country = Country.objects.get(name=country_name)
        except Country.DoesNotExist:
            return Response({'success': False, 'detail': 'such a country does not exist !!!'})

        try:
            state = State.objects.get(state=state_name, country=country)
        except State.DoesNotExist:
            return Response({'success': False, 'detail': 'There is no state in such a country !!!'})

        try:
            city = City.objects.get(city=city_name, state=state.id)
            if phone_number:
                title.phone_number = phone_number
            if postal_code:
                title.postal_code = postal_code
            if street_address:
                title.street_address = street_address
            if house_number:
                title.house_number = house_number
            if city:
                title.city = city
            if state:
                title.state = state
            if country:
                title.country = country
            title.save()
            return Response({'success': True, 'detail': 'Update successfully !'})
        except City.DoesNotExist:
            return Response({'success': False, 'detail': 'There is no city in such a state !!!'})

    def delete(self, request, shipping_address_id):
        user = request.user.id

        if not user:
            return Response({'success': False, "error": "user_id is required"})

        try:
            exists_data = ShippingAddress.objects.get(
                user=request.user.id,
                pk=shipping_address_id
            )
            if exists_data:
                exists_data.delete()
            return Response({'success': True, 'detail': 'Data deleted !'})
        except ShippingAddress.DoesNotExist:
            return Response({'success': False})


class DiscountCategoryListAPIView(GenericAPIView):
    serializer_class = DiscountCategoryListserializer

    def get(self, request):
        discount_category_data = DiscountCategory.objects.filter(start_time__lte=now())
        serializer = DiscountCategoryListserializer(discount_category_data, many=True)
        return Response(serializer.data)


class DiscountProductListAPIView(GenericAPIView):
    serializer_class = DiscountProductListSerializer

    def get(self, request):
        discount_products = DiscountProduct.objects.filter(start_time__lte=now())

        if not discount_products.exists():
            return Response({'success': False, 'error': 'No discount products found.'}, status=404)

        serializer = DiscountProductListSerializer(discount_products, many=True)
        return Response(serializer.data)
