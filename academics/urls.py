from django.urls import include, path
from rest_framework.routers import DefaultRouter

from academics.views import (
    AcademicYearViewSet,
    ClassChangeRequestViewSet,
    ClassViewSet,
    LevelViewSet,
    StudentViewSet,
    SubjectViewSet,
    TeachingAssignmentViewSet,
)

router = DefaultRouter()
router.register('academic-years', AcademicYearViewSet, basename='academic-years')
router.register('levels', LevelViewSet, basename='levels')
router.register('subjects', SubjectViewSet, basename='subjects')
router.register('classes', ClassViewSet, basename='classes')
router.register('students', StudentViewSet, basename='students')
router.register('teaching-assignments', TeachingAssignmentViewSet, basename='teaching-assignments')
router.register('class-change-requests', ClassChangeRequestViewSet, basename='class-change-requests')

urlpatterns = [
    path('', include(router.urls)),
]
