from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import serializers
from authapp.models import CustomUserModel
from django.contrib.auth.password_validation import validate_password
from django.conf import settings
import random

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    class Meta:
        model = CustomUserModel
        fields = ("id", "email", "username", "password","phone_number")
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        user = CustomUserModel.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
            phone_number=validated_data["phone_number"]
        )

        # Generate OTP
        otp = random.randint(10000, 99999)
        user.otp = otp
        user.otp_expiry = timezone.now() + timezone.timedelta(minutes=10)
        print(user.otp_expiry)
        user.max_otp_try = settings.MAX_OTP_TRY
        user.save()

        # Send OTP to email
        send_mail(
            'OTP Verification',
            f'Your OTP is: {otp}',
            settings.EMAIL_HOST_USER,  # Sender's email address
            [validated_data["email"]],  # Recipient's email address
            fail_silently=False,
        )
        print(user)
        return user

class OTPVerificationSerializer(serializers.Serializer):
    username = serializers.CharField()
    otp = serializers.CharField(min_length=5, max_length=5)
