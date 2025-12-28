from django.urls import path, include
from todo.views import (
 TaskList,
 TaskCreate,
 TaskDeleteView,
 TaskUpdateView,
 TaskDetailView,
 TaskToggelView)

app_name = "todo"

urlpatterns = [
 
    path("",TaskList.as_view(),name="task_list"),
    path("create/",TaskCreate.as_view(),name="todo_create"),
    path("detail/<int:pk>/",TaskDetailView.as_view(),name="todo_detail"),
    path("edit/<int:pk>/",TaskUpdateView.as_view(),name="task_edit"),
    path("delete/<int:pk>/",TaskDeleteView.as_view(),name="delete_task"),
    path("toggel/<int:pk>/", TaskToggelView.as_view(), name="toggel_task"),
]
