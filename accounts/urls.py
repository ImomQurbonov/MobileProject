from django.urls import path

from accounts.views import RegisterAPIView, UserInfoAPIView, LogoutAPIView, GoogleLogin, RedirectToGoogleAPIView, \
    callback_google, FacebookLogin, RedirectToFacebookApiView, callback_facebook, PasswordResetRequestView, \
    PasswordResetConfirmView


urlpatterns = [
    path('register', RegisterAPIView.as_view(), name='register'),
    path('logout', LogoutAPIView.as_view(), name='logout'),
    path('user-info', UserInfoAPIView.as_view(), name='user_info'),

    # Google
    path('google', GoogleLogin.as_view(), name='google_login'),
    path('google-login', RedirectToGoogleAPIView.as_view(), name='google_login2'),
    path('google/callback', callback_google, name='google_callback'),

    # Facebook
    path('facebook', FacebookLogin.as_view(), name='facebook'),
    path('facebook-login', RedirectToFacebookApiView.as_view(), name='facebook-login'),
    path('facebook/callback', callback_facebook, name='facebook_callback'),

    path('reset-password', PasswordResetRequestView.as_view(), name='password_reset_request')
    # path('reset-password-confirm/<str:uidb64>/<str:token>/', PasswordResetConfirmView.as_view(),
    #      name='reset_password_confirm')
]
