from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class CustomAuthenticationBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        UserModel = get_user_model()
     
        if email is None:
            
            email = kwargs.get(UserModel.USERNAME_FIELD)
           
        try:
            user = UserModel._default_manager.get(username=email)
        
            
            if user.check_password(password):
                
                return user
        except UserModel.DoesNotExist:
           
            return None
        return None  

    def user_can_authenticate(self, user):
        return True