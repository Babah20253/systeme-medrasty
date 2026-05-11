from django.urls import include, path
from rest_framework.routers import DefaultRouter

from schools.views import SchoolViewSet

router = DefaultRouter()
router.register('', SchoolViewSet, basename='schools')

urlpatterns = [
    path('', include(router.urls)),
]
