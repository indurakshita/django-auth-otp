# models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import RegexValidator
from django.conf import settings
from django.contrib.auth.models import PermissionsMixin


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password, **extra_fields):
        
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')
        

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        

        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, password):
        user = self.create_user(email,username,password)
        user.is_active = True   
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
        


class CustomUserModel(AbstractBaseUser,PermissionsMixin):
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    email_regex = RegexValidator(regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', message="Enter a valid email address.")

    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(verbose_name='email', max_length=255, unique=True, validators=[email_regex])
    phone_number = models.CharField(verbose_name='phone number', max_length=20, unique=True, validators=[phone_regex])
    is_active = models.BooleanField(default=False)
    is_staff= models.BooleanField(default=False)
    otp = models.CharField(max_length=6)
    otp_expiry = models.TimeField(null=True,blank=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    max_otp_try = models.CharField(max_length=2,default=settings.MAX_OTP_TRY)
    otp_max_out = models.DateTimeField(null=True,blank=True)
    user_register_at = models.DateTimeField(auto_now_add=True)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        db_table = 'auth_user'
        
    def __str__(self):
        return self.email
    
    