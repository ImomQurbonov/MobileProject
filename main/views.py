import datetime
import os

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import (
    CreateAPIView, ListAPIView,
    GenericAPIView, RetrieveUpdateDestroyAPIView,
    RetrieveAPIView, DestroyAPIView
)
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import AdminPermission
from accounts.serializers import User
from customer.models import ShippingAddress
from .models import (
    Product, Color,
    Category, Size,
    File, ProductSizeColor,
    Order, UserWallet,
    ShoppingCart, PromoCode,
    ReviewModel, LikeModel
)
from .serializers import (
    CreateProductSerializer, ProductListSerializer,
    CategorySerializer, ColorSerializer,
    SizeSerializer, FileUploadSerializer,
    ProductAddSizeColorSerializer, GetProductSizeColorSerializer,
    AddCategorySerializer, GetSizeColorSerializer,
    GetProductSizeSerializer, TemporarilyPhotosSerializer,
    AddToShoppingCartSerializer, FilterQuerySerializer,
    PromoCodeSerializer, QuerySerializer,
    ReviewSerializersRes, ReviewSerializer,
    LikeSerializersRes, ProductFileSerializer,
    CreateOrderSerializer, GetOrderSerializer,
    UpdateOrderSerializer, PaymentSerializer,
    UserWalletSerializer
)


class CreateProductAPIView(CreateAPIView):
    permission_classes = (IsAuthenticated, AdminPermission)
    serializer_class = CreateProductSerializer

    def post(self, request):
        product_serializer = self.serializer_class(data=request.data)
        if product_serializer.is_valid():
            product_instance = product_serializer.save()
            product = ProductListSerializer(product_instance)
            return Response(product.data)
        else:
            return Response({'message': 'Product data invalid'})


class GetProductsByCategoryIdAPIView(GenericAPIView):
    permission_classes = ()
    serializer_class = ProductListSerializer

    def get(self, request, category_id):
        try:
            product_data = Product.objects.filter(category_id=category_id)
            product_serializer = ProductListSerializer(product_data, many=True)
            return Response(data=product_serializer.data, status=200)
        except Exception as e:
            return Response(status=401, data=f'{e}')


class ProductUpdateAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, AdminPermission)
    serializer_class = CreateProductSerializer
    queryset = Product.objects.all()

    def get(self, request, pk):
        try:
            product_instance = self.get_object()
            if product_instance:
                serializer = ProductListSerializer(product_instance)
                return Response(serializer.data)
            else:
                return Response({'message': 'Product not found!'}, status=404)
        except Exception as e:
            return Response({'message': str(e)}, status=400)

    def put(self, request, pk):
        try:
            product_instance = self.get_object()
            if product_instance:
                serializer = self.serializer_class(instance=product_instance, data=request.data)
                if serializer.is_valid():
                    updated_product = serializer.save()
                    product_serializer = ProductListSerializer(updated_product)
                    return Response(product_serializer.data)
                else:
                    return Response({'message': 'Product input invalid !'}, status=400)
            else:
                return Response({'message': 'Product not found!'}, status=404)
        except Exception as e:
            return Response({'message': str(e)}, status=400)

    def patch(self, request, pk):
        try:
            product_instance = self.get_object()  # Retrieve the product instance
            if product_instance:
                product_instance.name = request.POST.get('name', product_instance.name)
                product_instance.description = request.POST.get('description', product_instance.description)
                product_instance.price = request.POST.get('price', product_instance.price)
                product_instance.category = request.POST.get('category', product_instance.category)
                product_instance.save()

                # Pass the instance and data to the serializer
                product_serializer = self.serializer_class(instance=product_instance, data=request.data)
                if product_serializer.is_valid():
                    product = product_serializer.save()
                    product_serializer = ProductListSerializer(product)
                    return Response(product_serializer.data)
                else:
                    return Response(product_serializer.errors, status=400)
            else:
                return Response({'message': 'Product not found!'}, status=404)
        except Exception as e:
            return Response({'message': str(e)}, status=400)


class CreateCategoryAPIView(CreateAPIView):
    queryset = Category.objects.all()
    permission_classes = (IsAuthenticated, AdminPermission)
    serializer_class = AddCategorySerializer


class CategoryGetAPIView(RetrieveAPIView):
    queryset = Category.objects.all()
    permission_classes = ()
    serializer_class = CategorySerializer


class CategoryListAPIView(ListAPIView):
    queryset = Category.objects.all()
    permission_classes = ()
    serializer_class = CategorySerializer


class ColorListAPIView(ListAPIView):
    queryset = Color.objects.all()
    permission_classes = ()
    serializer_class = ColorSerializer


class SizeListAPIView(ListAPIView):
    queryset = Size.objects.all()
    permission_classes = ()
    serializer_class = SizeSerializer


class SizeGetAPIView(RetrieveAPIView):
    queryset = Size.objects.all()
    permission_classes = ()
    serializer_class = SizeSerializer


class FileUploadAPIView(GenericAPIView):
    parser_classes = (MultiPartParser, FormParser, FileUploadParser)
    serializer_class = FileUploadSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ProductFileGetDelete(APIView):
    parser_classes = (MultiPartParser, FormParser, FileUploadParser)
    permission_classes = ()
    serializer_class = ProductFileSerializer

    def get(self, request, hash_code):
        file_instance = get_object_or_404(File, hash=hash_code)
        file_serializer = self.serializer_class(file_instance)
        return Response(file_serializer.data)

    def delete(self, request, hash_code):
        try:
            file_instance = File.objects.get(hash=hash_code)
        except File.DoesNotExist:
            return Response({'message': 'File not found'}, status=status.HTTP_404_NOT_FOUND)

        file_path = file_instance.file.path
        if os.path.exists(file_path):
            os.remove(file_path)
            file_instance.delete()
            return Response({"message": "File deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'message': 'File not found'}, status=status.HTTP_404_NOT_FOUND)


class GetProductSizesAPIView(GenericAPIView):
    permission_classes = ()
    serializer_class = ProductAddSizeColorSerializer
    queryset = ProductSizeColor.objects.all()

    def get(self, request, pk):
        try:
            product_detail = ProductSizeColor.objects.filter(product_id=pk)
            product_detail_serializer = GetProductSizeSerializer(product_detail, many=True)
            return Response(product_detail_serializer.data)
        except Exception as e:
            return Response({'detail': f'{e}'}, status=401)


class GetColorByProductSizeIdAPIView(APIView):
    permission_classes = ()

    def get(self, request):
        try:
            product_id = request.GET.get('product_id')
            size_id = request.GET.get('size_id')

            if product_id is not None and size_id is not None:
                data = ProductSizeColor.objects.filter(Q(product_id=product_id) & Q(size_id=size_id))
                data_serializer = GetSizeColorSerializer(data, many=True)
                return Response(data_serializer.data)
            else:
                return Response({"detail": "product_id and size_id parameters are required."}, status=400)
        except Exception as e:
            return Response(data=f'{e}', status=500)


class AddProductSizeColorAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated, AdminPermission)
    serializer_class = ProductAddSizeColorSerializer

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response({'detail': f'{e}'})


class AllProductSizeColorAPIView(GenericAPIView):
    permission_classes = ()
    serializer_class = GetProductSizeColorSerializer

    def get(self, request):
        data = ProductSizeColor.objects.all()
        data_serializer = self.serializer_class(data, many=True)
        return Response(data_serializer.data)


@receiver(post_save, sender=Product)
def update_category_count(sender, instance, created, **kwargs):
    if created:
        category = instance.category
        if category:
            category.count_product = Product.objects.filter(category=category).count()
            category.save()


class ProductListByOtherCategoryAPIView(APIView):
    permission_classes = ()

    def get(self, request):
        try:
            categories = Category.objects.all()
            data = []
            for category in categories:
                product = Product.objects.filter(category_id=category.id).first()
                if product:
                    product_serializer = ProductListSerializer(product)
                    data.append(product_serializer.data)
            return Response(data=data)
        except Exception as e:
            return Response({'detail': str(e)})


class GetTopProductsByCategoryAPIView(GenericAPIView):
    permission_classes = ()
    serializer_class = ProductListSerializer

    def get(self, request, category_id):
        try:
            product = Product.objects.filter(category_id=category_id).order_by('-sold_quantity')
            product_serializer = self.serializer_class(product, many=True)
            return Response(product_serializer.data)
        except Exception as e:
            return Response({'error': f'{e}'})


class GetNewArrivalsProductAPIView(GenericAPIView):
    permission_classes = ()
    serializer_class = ProductListSerializer

    def get(self, request):
        try:
            three_days_ago = datetime.datetime.now() - datetime.timedelta(days=3)
            data = Product.objects.filter(created_at__gte=three_days_ago)
            data_serializer = self.serializer_class(data, many=True)
            return Response(data_serializer.data)
        except Exception as e:
            return Response({'detail': str(e)})


class GetPopularProductAPIView(GenericAPIView):
    permission_classes = ()
    serializer_class = ProductListSerializer

    def get(self, request):
        try:
            data = Product.objects.filter(rate__gte=3).order_by('-rate')
            product_serializer = self.serializer_class(data, many=True)
            return Response(product_serializer.data)
        except Exception as e:
            return Response({'error': f'{e}'})


class AddToShoppingCartAPIView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AddToShoppingCartSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data.get('product_id')
            count_product = serializer.validated_data.get('count_product')
            user = request.user.id
            if ShoppingCart.objects.filter(product_id=product_id, user_id=user).exists():
                return Response({"message": "Product already exists in the shopping cart."},
                                status=status.HTTP_400_BAD_REQUEST)
            ShoppingCart.objects.create(product_id=product_id, user_id_id=user, count_product=count_product)
            return Response({"message": "Product added to the shopping cart successfully."},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShoppingCartListUpdateDelete(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AddToShoppingCartSerializer

    def get(self, request):
        user_id = request.user.id
        shopping_cart_detail = ShoppingCart.objects.filter(user_id=user_id)
        print(shopping_cart_detail.values())
        if shopping_cart_detail:
            data = []
            for item in shopping_cart_detail.values():
                product = Product.objects.get(id=item.get('product_id_id'))
                if product:
                    product_serializer = ProductListSerializer(product)
                    data.append(product_serializer.data)
            return Response(data=data)
        else:
            return Response({"message": "Shopping cart is empty."}, status=404)


class DeleteShoppingCartAPIView(DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AddToShoppingCartSerializer

    def delete(self, request, product_id):
        user_id = request.user.id
        if product_id:
            if ShoppingCart.objects.filter(product_id=product_id, user_id=user_id).exists():
                try:
                    ShoppingCart.objects.get(Q(user_id_id=user_id) & Q(product_id=product_id)).delete()
                    return Response(status=201)
                except Exception as e:
                    return Response({'message': 'Product not found', 'error': f'{e}'}, status=404)
            else:
                return Response({'message': 'Product in Shopping cart not found !'})
        else:
            return Response({'message': 'product_id invalid !'})


class SearchCategoryAPIView(GenericAPIView):
    permission_classes = ()
    serializer_class = CategorySerializer

    def get(self, request):
        query = request.query_params.get('query')
        if not query:
            return Response({'message': 'Query not provided'}, status=400)

        categories = Category.objects.filter(name__icontains=query)
        if categories.exists():
            serializer = self.serializer_class(categories, many=True)
            return Response(serializer.data)
        else:
            return Response({'message': 'No categories found for the query'}, status=404)


class FilterProductsAPIView(GenericAPIView):
    serializer_class = ProductListSerializer

    @swagger_auto_schema(query_serializer=FilterQuerySerializer)
    def get(self, request):
        category_id = request.GET.get('category_id')
        start_price = request.GET.get('start_price')
        end_price = request.GET.get('end_price')
        sort = request.GET.get('sort')
        rate = request.GET.get('rate')

        query = Product.objects.all()

        try:
            if category_id:
                query = query.filter(category_id=category_id)
            if start_price and end_price:
                query = query.filter(price__gte=start_price, price__lte=end_price)
            if sort:
                if sort == 'New_Today':
                    query = query.filter(created_at__day=datetime.datetime.now() - datetime.timedelta(days=1))
                elif sort == 'New_This_Week':
                    query = query.filter(created_at__day=datetime.datetime.now() - datetime.timedelta(days=7))
                elif sort == 'Top_sellers':
                    query = query.filter(sold_quantity__gte=2).order_by('-sold_quantity')
            if rate:
                query = query.filter(rate__gte=rate)
            query_serializer = self.serializer_class(query, many=True)
            return Response(query_serializer.data)
        except Exception as e:
            return Response({'error': str(e)})


class PromoCodeAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PromoCodeSerializer

    @swagger_auto_schema(query_serializer=QuerySerializer)
    def get(self, request):
        query = request.query_params.get('query')
        try:
            promo_code = PromoCode.objects.get(code=query)
        except PromoCode.DoesNotExist:
            return Response({'message': 'PromoCode not found'}, status=status.HTTP_404_NOT_FOUND)

        if promo_code.start_date > timezone.now():
            return Response({'message': 'PromoCode is not active yet'}, status=status.HTTP_400_BAD_REQUEST)

        if promo_code.end_date < timezone.now():
            return Response({'message': 'PromoCode expired'}, status=status.HTTP_400_BAD_REQUEST)
        promo_code.current_usage += 1
        promo_code.save()
        data_serializer = self.serializer_class(promo_code)
        return Response(data_serializer.data)


class UpdateShoppingCartAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AddToShoppingCartSerializer

    def patch(self, request):
        user_id = request.user.id
        product_id = request.data.get('product_id')
        count_product = request.data.get('count_product')
        shopping_cart_item = get_object_or_404(ShoppingCart, product_id_id=product_id, user_id_id=user_id)

        shopping_cart_item.count_product = int(count_product)
        shopping_cart_item.save()

        serializer = self.serializer_class(shopping_cart_item)
        return Response(serializer.data)


class CreateOrderAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            user_id = request.user.id

            if not ShippingAddress.objects.filter(user_id=user_id).exists():
                return Response({'message': 'Shipping address not found!'}, status=status.HTTP_404_NOT_FOUND)

            shipping_address = ShippingAddress.objects.get(user_id=user_id)
            products = ShoppingCart.objects.filter(user_id=user_id)
            data = []

            if not products.exists():
                return Response({'message': 'Shopping cart is empty!'}, status=status.HTTP_400_BAD_REQUEST)

            for product_cart in products:
                order = Order.objects.create(
                    shipping_address=shipping_address,
                    product=product_cart.product_id,
                    user_id=user_id,
                    count_product=product_cart.count_product
                )
                serializer = CreateOrderSerializer(order)
                data.append(serializer.data)

            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GetOrderAPIView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = GetOrderSerializer

    def get(self, request):
        user_id = request.user.id
        try:
            data = Order.objects.filter(user_id=user_id)
            data_serializer = self.serializer_class(data, many=True)
            return Response(data=data_serializer.data)
        except Exception as e:
            return Response({'message': f'{e}'})


class UpdateUserOrderAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UpdateOrderSerializer

    def patch(self, request):
        user_id = request.user.id
        product_id = request.data.get('product')

        data = Order.objects.filter(Q(user_id=user_id) and Q(product=product_id))
        if data:
            for x in data:
                x.status = 'completed'
                x.save()
            data_serializer = GetOrderSerializer(data, many=True)
            return Response(data_serializer.data, status=201)
        else:
            return Response({'message': 'Order not Found!'}, status=404)


@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        UserWallet.objects.create(user=instance)


class PaymentAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PaymentSerializer

    def post(self, request):
        user_id = request.user.id
        try:
            user_wallet = UserWallet.objects.get(user_id=user_id)
            products_cash = request.data.get('cash')
            if user_wallet.cash >= products_cash:
                user_wallet.cash -= products_cash
                user_wallet.save()
                return Response({'message': 'Payment completed!'})
            else:
                return Response({'message': 'In Your Wallet not enough money!'})
        except Exception as e:
            return Response({'message': f'{e}'})


class GetUserWalletAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            user_id = request.user.id
            user_wallet = UserWallet.objects.get(user_id=user_id)
            if user_wallet:
                user_wallet_serializer = UserWalletSerializer(user_wallet)
                return Response(user_wallet_serializer.data)
        except ObjectDoesNotExist as e:
            return Response({'message': 'User Wallet not found!'})


class Review(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ReviewSerializer

    def post(self, request, pk):
        user = request.user.id
        comment = request.data.get('comment')
        star = request.data.get('star')

        rev = ReviewModel.objects.create(
            user_id=user,
            product_id=pk,
            comment=comment,
            star=star
        )
        review_serializers = ReviewSerializersRes(rev)
        return Response({'success': True, 'data': review_serializers.data})

    def patch(self, request, pk):
        user_id = request.user.id
        comment = request.data.get('comment')
        rev = ReviewModel.objects.update(
            user_id=user_id,
            product_id=pk,
            comment=comment
        )
        response = ReviewSerializersRes(rev)
        return Response({'success': True, 'data': response.data})

    def delete(self, request, pk):
        user_id = request.user.id

        LikeModel.objects.filter(user_id=user_id, product_id=pk).delete()
        return Response({'success': True})


class Like(GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        user = request.user.id
        like = LikeModel.objects.create(
            user_id=user,
            product_id=pk,
            like=1
        )
        like_serializers = LikeSerializersRes(like)
        return Response({'success': True, 'data': like_serializers.data})

    def delete(self, request, pk):
        user_id = request.user.id

        LikeModel.objects.filter(user_id=user_id, product_id=pk).delete()
        return Response({'success': True})


class GetSimilarProductsAPIView(GenericAPIView):
    permission_classes = ()
    serializer_class = TemporarilyPhotosSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            if serializer.is_valid():
                uploaded_file = serializer.validated_data['file']
                file_content = uploaded_file.read()
                with open(f'media/temporarily/{uploaded_file.name}', 'wb') as f:
                    f.write(file_content)
                similarity_percentage = check_image_similarity(uploaded_file.name)
                similar_products = []
                for products in similarity_percentage:
                    if float(list(products.values())[0]) > 50.0:
                        similar_products.append(products)

                similar_product_ids = []
                for filename in similar_products:
                    file_name = f'file/{list(filename.keys())[0]}'
                    try:
                        file_obj = File.objects.get(file__icontains=file_name)
                        if file_obj.product_id not in similar_product_ids:
                            similar_product_ids.append(file_obj.product_id)
                    except File.DoesNotExist:
                        pass

                similar_products_data = []
                for product_id in similar_product_ids:
                    try:
                        product = Product.objects.get(pk=product_id)
                        similar_products_data.append(product)
                    except Product.DoesNotExist:
                        pass

                serializer = ProductListSerializer(similar_products_data, many=True)

                return Response(serializer.data, status=status.HTTP_200_OK)

            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)


class ColorGetAPIView(RetrieveAPIView):
    queryset = Color.objects.all()
    permission_classes = ()
    serializer_class = ColorSerializer


class CreateColorAPIView(CreateAPIView):
    queryset = Color.objects.all()
    permission_classes = (IsAuthenticated, AdminPermission)
    serializer_class = ColorSerializer


class CreateSizeAPIView(CreateAPIView):
    queryset = Size.objects.all()
    permission_classes = (IsAuthenticated, AdminPermission)
    serializer_class = SizeSerializer
