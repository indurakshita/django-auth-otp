from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from authapp.models import CustomUserModel
from authapp.serializers import ForgetPasswordSerializer, ForgetPasswordConfirmSerializer
import random
from datetime import datetime, timedelta

User = get_user_model()

class ForgetPasswordRequestAPIView(APIView):
    
    permission_classes = [AllowAny]
    serializer_class = ForgetPasswordSerializer
  
    
    last_otp_request = {}

    def post(self, request):
        email = request.data.get('email', '')
        
        # Check if there's a recent OTP request for this email
        last_request_time = self.last_otp_request.get(email)
        print(last_request_time)
        if last_request_time:
            # If the last request was less than a minute ago, reject the request
            if datetime.now() - last_request_time < timedelta(minutes=1):
                return Response({"message": "Please wait for some time before requesting another OTP"}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        serializer = self.serializer_class(
            data=request.data, 
            context={'request': request, 'view': self}
        )
        if serializer.is_valid():
            user = serializer.save()
            if user:
                # Update the last OTP request timestamp
                self.last_otp_request[email] = datetime.now()
                return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Throttled. Please wait before sending another OTP."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        error = [f"{field} {error}" for field, errors in serializer.errors.items() for error in errors][0]
        return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

class ForgetPasswordConfirmAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ForgetPasswordConfirmSerializer
    
    def post(self, request):
        user = request.user
        serializer = self.serializer_class(data=request.data,context={'user': user})
        if serializer.is_valid():
            otp = serializer.validated_data.get('otp')
            password = serializer.validated_data.get('password')

            user = User.objects.filter(otp=otp, otp_expiry__gt=timezone.now()).first()
         

            if user:
                user.set_password(password)
                user.save()
                
                    
                return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid OTP or OTP expired"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
