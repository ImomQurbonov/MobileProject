from django.urls import path

from main.views import *

urlpatterns = [
    path('add-product', CreateProductAPIView.as_view(), name='add-product'),
    path('add-category', CreateCategoryAPIView.as_view(), name='add-category'),
    path('add-color', CreateColorAPIView.as_view(), name='add-color'),
    path('add-size', CreateSizeAPIView.as_view(), name='add-size'),
    path('product-get-update-delete/<int:pk>', ProductUpdateAPIView.as_view(), name='product-get'),
    path('category-get/<int:pk>', CategoryGetAPIView.as_view(), name='category-get'),
    path('search-category/', SearchCategoryAPIView.as_view(), name='search-category'),
    path('color-get/<int:pk>', ColorGetAPIView.as_view(), name='color-get'),
    path('size-get/<int:pk>', SizeGetAPIView.as_view(), name='size-get'),
    path('get-product-sizes/<int:pk>', GetProductSizesAPIView.as_view(), name='get-product-sizes'),
    path('get-product-color-by-size-id/', GetColorByProductSizeIdAPIView.as_view(), name='get-product_color-by-size_id'),
    path('add-product-size-color', AddProductSizeColorAPIView.as_view(), name='add-product-size-color'),
    path('get-products-by-category_id/<int:category_id>', GetProductsByCategoryIdAPIView.as_view(), name='get-products'),
    path('get-product-files/<int:pk>', ProductFileGetDelete.as_view(), name='get-product-files'),
    path('get-product-files/<str:hash_code>', ProductFileGetDelete.as_view(), name='get-product-files'),
    path('get-categories', CategoryListAPIView.as_view(), name='get-categories'),
    path('get-colors', ColorListAPIView.as_view(), name='get-colors'),
    path('get-sizes', SizeListAPIView.as_view(), name='get-sizes'),
    path('upload-file/', FileUploadAPIView.as_view(), name='upload-file'),
    path('get-products-by-all-categories/', ProductListByOtherCategoryAPIView.as_view(), name='get-products-by-all-categories'),
    path('get-top-products-by-category-id/<int:category_id>', GetTopProductsByCategoryAPIView.as_view(), name='get-top-products'),
    path('get-new-arrivals-products', GetNewArrivalsProductAPIView.as_view(), name='get-top-products'),
    path('get-popular-products', GetPopularProductAPIView.as_view(), name='get-popular-products'),
    path('get-shopping-cart-products', ShoppingCartListUpdateDelete.as_view(), name='get-shopping-cart-products'),
    path('add-shopping_cart', AddToShoppingCartAPIView.as_view(), name='add-shopping_cart'),
    path('update-count-product-shopping_cart', UpdateShoppingCartAPIView.as_view(), name='update-count-product-shopping_cart'),
    path('delete-shopping_cart/<int:product_id>', DeleteShoppingCartAPIView.as_view(), name='delete-shopping_cart'),
    path('filter', FilterProductsAPIView.as_view(), name='filter'),
    path('promocode', PromoCodeAPIView.as_view(), name='promo_code'),
    path('order', CreateOrderAPIView.as_view(), name='order'),
    path('get-order', GetOrderAPIView.as_view(), name='get-order'),
    path('update-order', UpdateUserOrderAPIView.as_view(), name='update-order'),
    path('payment', PaymentAPIView.as_view(), name='payment'),
    path('user-wallet', GetUserWalletAPIView.as_view(), name='user-wallet'),
    # path('get-similar-products/', GetSimilarProductsAPIView.as_view(), name='similar-products')
]

