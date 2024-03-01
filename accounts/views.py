import os
import requests
from dotenv import load_dotenv
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.generics import GenericAPIView
from allauth.socialaccount.models import SocialApp
from django.contrib.auth.views import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from accounts.serializers import UserSerializer, UserRegisterSerializer, PasswordResetSerializer
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from main.tasks import send_email_reset

User = get_user_model()
load_dotenv()


class RegisterAPIView(GenericAPIView):
    serializer_class = UserRegisterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors)


# Log out
class LogoutAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response({"success": True}, status=status.HTTP_204_NO_CONTENT)


# User Info
class UserInfoAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get(self, request):
        user = request.user
        user_serializer = UserSerializer(user)
        return Response({'success': True, 'data': user_serializer.data})


# PasswordResetRequest
class PasswordResetRequestView(GenericAPIView):
    serializer_class = UserRegisterSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            send_email_reset.delay(
                email,
                uid,
                token,
            )
            return Response({'detail': 'Password reset link sent to your email.'}, status=202)
        else:
            return Response({'detail': 'Email not found.'}, status=404)


# PasswordResetConfirm
class PasswordResetConfirmView(GenericAPIView):
    serializer_class = PasswordResetSerializer

    def post(self, request, uidb64, token, *args, **kwargs):
        try:
            uidb64 = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uidb64)

            if default_token_generator.check_token(user, token):
                new_password = request.data.get('new_password', '')
                user.set_password(new_password)
                user.save()
                return Response({'detail': 'Password reset successful.'}, status=200)
            else:
                return Response({'detail': 'Invalid token.'}, status=400)
        except Exception as e:
            return Response({'detail': f'{e}.'}, status=400)


# Google sign-in
class RedirectToGoogleAPIView(APIView):
    def get(self, request):
        google_redirect_uri = os.getenv('GOOGLE_REDIRECT_URL')
        try:
            google_client_id = SocialApp.objects.get(provider='google').client_id
        except SocialApp.DoesNotExist:
            return Response({'success': False, 'message': 'SocialApp does not exist'}, status=404)
        url = f'https://accounts.google.com/o/oauth2/v2/auth?redirect_uri={google_redirect_uri}&prompt=consent&response_type=code&client_id={google_client_id}&scope=openid email profile&access_type=offline'
        return redirect(url)


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = 'https://c866-178-218-201-17.ngrok-free.app/accounts/google/callback'
    client_class = OAuth2Client


@api_view(["GET"])
def callback_google(request):
    code = request.GET.get("code")
    res = requests.post("https://c866-178-218-201-17.ngrok-free.app/accounts/google", data={"code": code}, timeout=30)
    return Response(res.json())


# facebook
class RedirectToFacebookApiView(APIView):
    def get(self, request):
        facebook_redirect_uri = os.getenv('FACEBOOK_REDIRECT_URI')
        facebook_app_id = os.getenv('FACEBOOK_APP_ID')
        try:
            url = f'https://www.facebook.com/v9.0/dialog/oauth?client_id={facebook_app_id}&redirect_uri={facebook_redirect_uri}&scope=email,public_profile'  # noqa
        except SocialApp.DoesNotExist:
            return Response({'success': False, 'message': 'Social does not exist'}, status=404)
        return redirect(url)


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter
    callback_url = "https://c866-178-218-201-17.ngrok-free.app/accounts/facebook/callback_facebook"
    client_class = OAuth2Client


@api_view(['GET'])
def callback_facebook(request):
    """Callback function to handle the Facebook OAuth2 callback."""
    code = request.query_params.get('code')
    if not code:
        return Response({'error': 'Code parameter is missing.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        response = requests.get("https://graph.facebook.com/v9.0/oauth/access_token", params={
            'client_id': os.getenv('FACEBOOK_APP_ID'),
            'redirect_uri': os.getenv('FACEBOOK_REDIRECT_URI'),
            'client_secret': os.getenv('FACEBOOK_APP_SECRET'),
            'code': code,
        })
        response.raise_for_status()
        data = response.json()
        access_token = data.get('access_token')

        if access_token:
            user_info_response = requests.get("https://graph.facebook.com/me", params={
                'fields': 'id,name,email',
                'access_token': access_token,
            })
            user_info_response.raise_for_status()
            user_info = user_info_response.json()

            return Response({'access_token': access_token, 'user_info': user_info}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Access token not found.'}, status=status.HTTP_400_BAD_REQUEST)
    except requests.exceptions.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# https://accounts.google.com/o/oauth2/v2/auth?redirect_uri=https://63b4-178-218-201-17.ngrok-free.app/accounts/google/callback&prompt=consent&response_type=code&client_id=796972424476-4pakur4pb1c0d578vgso2u72j3burqbh.apps.googleusercontent.com&scope=openid email profile&access_type=offline # noqa
# ngrok http http://localhost:8000
# https://www.facebook.com/v9.0/dialog/oauth?client_id=710566401221328&redirect_uri=https://45a7-178-218-201-17.ngrok-free.app/accounts/facebook/callback&scope=email,public_profile

class UserListAPiView(GenericAPIView):
    permission_classes = ()

    def get(self):
        pass
