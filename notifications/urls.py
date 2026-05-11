from django.urls import include, path
from rest_framework.routers import DefaultRouter

from notifications.views import OTPViewSet

router = DefaultRouter()
router.register('otp', OTPViewSet, basename='otp')

urlpatterns = [
    path('', include(router.urls)),
]
