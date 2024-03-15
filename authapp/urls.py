from django.urls import path, include
from authapp.views import SignupViewSet,VerifyOTPViewSet,LoginAPIView,ForgetPasswordRequestAPIView,ForgetPasswordConfirmAPIView


urlpatterns = [
    path('signup/', SignupViewSet.as_view({'post': 'create'}), name='signup-create'),
    path('signup/regenerate_otp/', SignupViewSet.as_view({'patch': 'regenerate_otp'}), name='signup-regenerate-otp'),
    path('signup/verify_otp/', VerifyOTPViewSet.as_view({"post":"create"}), name='signup-verify-otp'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('forgetpassword/', ForgetPasswordRequestAPIView.as_view(), name='forgetpassword'),
    path('forgetpassword/confirm/', ForgetPasswordConfirmAPIView.as_view(), name='forgetpassword'),
]