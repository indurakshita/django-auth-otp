import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()

class JWTAuthenticationBackend(BaseAuthentication):
    def authenticate(self, request, token=None):
        if token is None:
            auth_header = request.META.get('HTTP_AUTHORIZATION')
            if not auth_header:
                raise AuthenticationFailed('Authentication failed. Provide a valid token in the header.')
            token = auth_header
 
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            user = User.objects.get(pk=user_id)
            return (user, None) 
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found')
