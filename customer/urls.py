from django.urls import path

from customer.views import (
    ShippingAddressAPIView,
    MyFavouriteAPIView,
    DiscountProductListAPIView,
    DiscountCategoryListAPIView,
    ShippingAddressUpdateAPIView,
)

urlpatterns = [
    path('favourites/', MyFavouriteAPIView.as_view(), name='favourites'),
    path('shipping_address/', ShippingAddressAPIView.as_view(), name='shipping-address'),
    path('shipping_address_update/<int:shipping_address_id>/', ShippingAddressUpdateAPIView.as_view(),
         name='shipping-address-update'),
    path('discount_category_list/', DiscountCategoryListAPIView.as_view(), name='discount-product'),
    path('discount_product_list/', DiscountProductListAPIView.as_view(), name='discount-category-list')
]
