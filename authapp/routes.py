from rest_framework.routers import DefaultRouter
from authapp.views import SignupViewSet

router = DefaultRouter()

# router.register(r'signup', SignupViewSet,basename="signup")