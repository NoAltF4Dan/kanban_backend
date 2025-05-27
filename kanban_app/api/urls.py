from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import TaskCommentListCreateView, TaskCommentDeleteView, EmailCheckView, BoardViewSet, ColumnViewSet, TaskViewSet, CommentViewSet

router = DefaultRouter()
router.register(r'boards', BoardViewSet, basename='board')
router.register(r'columns', ColumnViewSet, basename='column')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path("tasks/<int:task_id>/comments/", TaskCommentListCreateView.as_view(), name="task-comments"),
    path("tasks/<int:task_id>/comments/<int:comment_id>/", TaskCommentDeleteView.as_view(), name="task-comment-delete"),
    path("email-check/", EmailCheckView.as_view(), name="email-check"),
] + router.urls