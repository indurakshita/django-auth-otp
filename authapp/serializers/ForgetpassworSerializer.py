from rest_framework import serializers
from django.contrib.auth import get_user_model
import re
import random
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from rest_framework.throttling import UserRateThrottle
from django.utils import timezone
from datetime import datetime
from django.core.exceptions import ValidationError


User = get_user_model()



class ForgetPasswordEmailThrottle(UserRateThrottle):
    rate = '1/m' 
    
    

class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
   
    def validate_email(self, value):
        email = value

        if User.objects.filter(email=email).exists():
            return value
        else:
            raise serializers.ValidationError("User not found")

    def create(self, validated_data):
        email = validated_data["email"]
        user = User.objects.get(email=email)
      
        # Generate OTP
        otp = random.randint(10000, 99999)
        user.otp = otp
        user.otp_expiry = timezone.now() + timezone.timedelta(minutes=10)
        user.max_otp_try = settings.MAX_OTP_TRY
        user.save()

        throttle = ForgetPasswordEmailThrottle()
        if throttle.allow_request(self.context['request'], self.context['view']):
            # Send OTP email
            send_mail(
                'OTP Verification for Forgetpassword',
                f'Your OTP is: {otp}',
                settings.EMAIL_HOST_USER,  
                [validated_data["email"]],
                fail_silently=False,
            )
            return user
        else:
            # Throttled
            return user  
    
    
    
class ForgetPasswordConfirmSerializer(serializers.Serializer):
    otp = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
        
    def validate(self, data):
        password = data.get('password')
        pattern = (
            r'^(?=.*[!@#$%^&*()_\-+=|\\~`{}\[\]:;"\'<>,.?\/])'  # at least one special character
            r'(?=.*[a-z])'  # at least one lowercase letter
            r'(?=.*[A-Z])'  # at least one uppercase letter
            r'(?=.*\d)'  # at least one digit
            r'.{8,}$'  # minimum length of 8 characters
        )

        if not re.match(pattern, password):
            raise serializers.ValidationError(
                "Password must contain at least one special character, "
                "one lowercase letter, one uppercase letter, and one digit, "
                "and be at least 8 characters long."
            )

        return data
    

        
    def validate(self, data):
        password = data.get('password')
        otp = data.get('otp')

        user = self.context.get('user')
        if not user:
            raise ValidationError("User not found in context.")

        otp_expiry = user.otp_expiry
        current_datetime = timezone.now()
        if otp_expiry is not None:
            otp_expiry_datetime = datetime.combine(datetime.now().date(), otp_expiry)
            if current_datetime > otp_expiry_datetime:
                raise ValidationError("OTP has expired.")
       
        
        return data

    def save(self):
        user = self.context['user']
        user.set_password(self.validated_data['password'])
        user.save()

