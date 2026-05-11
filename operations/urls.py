from django.urls import include, path
from rest_framework.routers import DefaultRouter

from operations.views import AbsenceViewSet, GradeViewSet, IncidentViewSet, SubjectCoefficientViewSet

router = DefaultRouter()
router.register('grades', GradeViewSet, basename='grades')
router.register('absences', AbsenceViewSet, basename='absences')
router.register('incidents', IncidentViewSet, basename='incidents')
router.register('subject-coefficients', SubjectCoefficientViewSet, basename='subject-coefficients')

urlpatterns = [
    path('', include(router.urls)),
]
