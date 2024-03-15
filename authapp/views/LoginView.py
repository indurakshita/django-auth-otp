from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from authapp.models import CustomUserModel
from authapp.serializers import UserLoginSerializer, CustomUserSerializer
import json
from authapp.utils import token_generation

class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer
    
    def post(self, request):
        data = request.data
        username = data.get('username')
        password = data.get('password')
        
        if not username :
            return Response({"error": "username is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not password:
            return Response({"error": "Password is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            if user.is_active:
                
                token=token_generation(user.id)
                user_profile_serializer = CustomUserSerializer(user)
                json_data=json.dumps(user_profile_serializer.data)
                data = json.loads(json_data)
                data['token'] = token
                return Response(data)
            else:
                return Response({"error": "User not activated"}, status=status.HTTP_400_BAD_REQUEST)
            
        elif CustomUserModel.objects.filter(username=username).exists():
            return Response({"error": "Incorrect password"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)
