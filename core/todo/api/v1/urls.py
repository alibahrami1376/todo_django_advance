from rest_framework.routers import DefaultRouter
from todo.api.v1.views import TaskModelViewSet

app_name = "api-v1"

router = DefaultRouter()
router.register("task", TaskModelViewSet, basename="task")

urlpatterns = router.urls

# urlpatterns = [
#     # path("task/<int:id>",task_detail,name="task-detaile"),
#     # path("list/",api_post_list_view,name="task-list"),
# #     path("list/",TaskList.as_view(),name="task-list"),
# #     path("task/<int:id>",TaskDetail.as_view(),name="task-detaile"),
# # ]
