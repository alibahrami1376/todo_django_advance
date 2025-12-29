from django.urls import path, include
from todo.views import (
 TaskListView,
 TaskCreateView,
 TaskDeleteView,
 TaskUpdateView,
 TaskDetailView,
 TaskToggleView)

app_name = "todo"

urlpatterns = [
 
    path("",TaskListView.as_view(),name="task_list"),
    path("create/",TaskCreateView.as_view(),name="create_task"),
    path("detail/<int:pk>/",TaskDetailView.as_view(),name="detail_task"),
    path("edit/<int:pk>/",TaskUpdateView.as_view(),name="edit_task"),
    path("delete/<int:pk>/",TaskDeleteView.as_view(),name="delete_task"),
    path("toggle/<int:pk>/", TaskToggleView.as_view(), name="toggle_task"),
]
