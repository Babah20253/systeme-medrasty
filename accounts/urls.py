from django.urls import include, path
from rest_framework.routers import DefaultRouter

from accounts.views import LoginView, PasswordResetViewSet, UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='account-users')
router.register('password-reset', PasswordResetViewSet, basename='password-reset')

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('', include(router.urls)),
]
