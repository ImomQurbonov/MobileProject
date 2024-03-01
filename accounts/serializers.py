from rest_framework import serializers
from django.contrib.auth.views import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'username', 'date_joined')


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField()
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password', 'password_confirm', 'date_joined')

    def create(self, validated_data):
        if validated_data['password'] == validated_data['password_confirm']:
            if User.objects.filter(email=validated_data['email']).exists():
                raise serializers.ValidationError('Email already exists!')
            if User.objects.filter(username=validated_data['username']).exists():
                raise serializers.ValidationError('Username already exists!')
            validated_data.pop('password_confirm')
            user = User.objects.create_user(**validated_data)
            return user
        else:
            raise serializers.ValidationError('Password are not found!')


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(max_length=20)
