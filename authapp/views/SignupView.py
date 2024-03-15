import datetime
import random
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from authapp.models import CustomUserModel
from authapp.serializers import CustomUserSerializer, OTPVerificationSerializer

class SignupViewSet(ModelViewSet):
    queryset = CustomUserModel.objects.all()
    serializer_class = CustomUserSerializer
    
    def create(self,request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        error = [f"{field} {error}" for field, errors in serializer.errors.items() for error in errors][0]
        return Response({"error":error}, status=status.HTTP_400_BAD_REQUEST) 
    
    @action(detail=False, methods=['patch'])
    def regenerate_otp(self, request):
        email = request.data.get('email')
        
        try:
            user = CustomUserModel.objects.get(email=email)
            if int(user.max_otp_try) == 0 and user.otp_max_out and timezone.now() < user.otp_max_out:
                return Response({'error': 'Max OTP try reached, try again later'}, status=status.HTTP_400_BAD_REQUEST)
            
            otp = random.randint(10000, 99999)
            otp_expiry = timezone.now() + datetime.timedelta(minutes=10)
            max_otp_try = int(user.max_otp_try)- 1
            
            user.otp = otp
            user.otp_expiry = otp_expiry
            user.max_otp_try = max_otp_try
            
            if max_otp_try == 0:
                user.otp_max_out = timezone.now() + datetime.timedelta(hours=1)
            elif max_otp_try == -1:
                user.max_otp_try = settings.MAX_OTP_TRY
            else:
                user.otp_max_out = None
            
            user.save()
            
            send_mail(
                'Your OTP',
                f'Your OTP is: {otp}',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            return Response({'message': 'OTP regenerated successfully'}, status=status.HTTP_200_OK)
        except CustomUserModel.DoesNotExist:
            return Response({'error': 'User with provided email not found'}, status=status.HTTP_404_NOT_FOUND)
        

class VerifyOTPViewSet(ModelViewSet):
    queryset = CustomUserModel.objects.all()
    serializer_class = OTPVerificationSerializer

    @action(detail=False, methods=['post'])
    def create(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            otp = serializer.validated_data['otp']
            try:
                user = CustomUserModel.objects.get(username=username)
                if user.is_active:
                    return Response({'error': 'User account is already activated'}, status=status.HTTP_400_BAD_REQUEST)
                elif user.otp == otp and user.otp_expiry and timezone.now().time() < user.otp_expiry:
                    user.is_active = True
                    user.save()
                    return Response({'message': 'user created successfully'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid OTP or OTP expired'}, status=status.HTTP_400_BAD_REQUEST)
                
            except CustomUserModel.DoesNotExist:
                return Response({'error': 'User with provided email not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            error = [f"{field} {error}" for field, errors in serializer.errors.items() for error in errors][0]
            return Response({"error":error}, status=status.HTTP_400_BAD_REQUEST) 

    
    