from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import TaskCommentCreateView, TaskCommentListView, EmailCheckView, TasksAssignedToMeView, BoardViewSet, ColumnViewSet, TaskViewSet, CommentViewSet

router = DefaultRouter()
router.register(r'boards', BoardViewSet, basename='board')
router.register(r'columns', ColumnViewSet, basename='column')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'comments', EmailCheckView, basename='email-check')
router.register(r'comments', TaskCommentListView, basename='task-comments')
router.register(r'comments', TaskCommentCreateView, basename='task-comments-post')

urlpatterns = [
    path("tasks/assigned-to-me/", TasksAssignedToMeView.as_view(), name="tasks-assigned-to-me"),
] + router.urls