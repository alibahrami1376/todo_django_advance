from rest_framework.permissions import IsAuthenticated
from todo.models import Task
from todo.api.v1.serializers import TaskSerializer
from rest_framework import viewsets
from todo.api.v1.permission import IsTaskOwner
from todo.api.v1.paginations import DefaultPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class TaskModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsTaskOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering_fields = ["created_date"]
    search_fields = ["title", "description"]
    filterset_fields = {"complete": ["exact"]}
    serializer_class = TaskSerializer
    pagination_class = DefaultPagination

    def get_queryset(self):
        profile = getattr(self.request.user, "profile", None)
        if not profile:
            return Task.objects.none()
        return Task.objects.filter(user=profile)
