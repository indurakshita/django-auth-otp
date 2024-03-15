from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()


class UserLoginSerializer(serializers.Serializer):
    
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})

    # def validate(self, data):
    #     username = data.get('username')
    #     password = data.get('password')
     

    #     if username and password:
    #         # Authenticate the user
    #         user = authenticate(request=self.context.get('request'), username=username, password=password)
    #         if user:
    #             # Check if the user account is active
    #             if not user.is_active:
    #                 raise serializers.ValidationError("User account is disabled.")
    #             return user
    #         else:
    #             raise serializers.ValidationError("Invalid login credentials.", code='invalid_credentials')
    #     else:
    #         raise serializers.ValidationError("Must include 'username' and 'password'.", code='invalid_credentials')
