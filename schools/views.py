from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsSuperAdmin
from schools.models import School
from schools.serializers import SchoolCreateWithDirectorSerializer, SchoolSerializer


class SchoolViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
	queryset = School.objects.all().order_by('-created_at')
	permission_classes = [IsAuthenticated, IsSuperAdmin]

	def get_serializer_class(self):
		if self.action == 'create':
			return SchoolCreateWithDirectorSerializer
		return SchoolSerializer

	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		school = serializer.save()
		return Response(SchoolSerializer(school).data, status=status.HTTP_201_CREATED)
