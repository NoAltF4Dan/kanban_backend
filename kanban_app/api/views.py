from django.shortcuts import render, get_object_or_404
from rest_framework import status, generics, permissions
from rest_framework.generics import DestroyAPIView
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied

from .serializers import BoardDetailSerializer, CommentSerializer, BoardSerializer, ColumnSerializer, TaskSerializer
from kanban_app.models import Comment, Board, Column, Task
from .permissions import IsOwnerOrReadOnly

from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

class BoardViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    queryset = Board.objects.all()

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(
            Q(owner=user) | Q(members=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_serializer_class(self):
        if self.action in ["retrieve", "update", "partial_update"]:
            return BoardDetailSerializer
        return BoardSerializer

class ColumnViewSet(ModelViewSet):
    serializer_class    = ColumnSerializer
    permission_classes  = [IsAuthenticated]

    def get_queryset(self):
        user     = self.request.user
        qs       = Column.objects.all()
        board_id = self.request.query_params.get("board")
        if board_id:
            qs = qs.filter(board_id=board_id)
        return qs.filter(Q(board__owner=user) | Q(board__members=user))

    def _check_board_access(self, board):
        user = self.request.user
        if not (board.owner == user or user in board.members.all()):
            raise PermissionDenied("Du musst Mitglied dieses Boards sein.")

    def perform_create(self, serializer):
        board = serializer.validated_data["board"]
        self._check_board_access(board)
        serializer.save()

    def perform_update(self, serializer):
        board = serializer.instance.board
        self._check_board_access(board)
        serializer.save()

    def perform_destroy(self, instance):
        board = instance.board
        self._check_board_access(board)
        instance.delete()

class TaskViewSet(ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(
            Q(board__owner=user) | Q(board__members=user)
        )

    def _check_board_access(self, board):
        user = self.request.user
        if not (board.owner == user or user in board.members.all()):
            raise PermissionDenied("Du musst Mitglied dieses Boards sein.")

    def perform_create(self, serializer):
        board = serializer.validated_data['board']
        self._check_board_access(board)
        serializer.save()

    def perform_update(self, serializer):
        board = serializer.instance.board
        self._check_board_access(board)
        serializer.save()

    def perform_destroy(self, instance):
        board = instance.board
        self._check_board_access(board)
        instance.delete()

    @action(detail=False, methods=['get'], url_path='assigned-to-me')
    def assigned_to_me(self, request):
        tasks = self.get_queryset().filter(assignee=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='reviewing')
    def reviewing(self, request):
        tasks = self.get_queryset().filter(reviewer=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
   
class EmailCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.query_params.get("email")
        if not email:
            return Response({"error": "Email is required."}, status=400)

        try:
            user = User.objects.get(email=email)
            return Response({
                "id": user.id,
                "email": user.email,
                "fullname": user.get_full_name()
            })
        except User.DoesNotExist:
            return Response({}, status=200)
        
class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("Du darfst nur deine eigenen Kommentare löschen.")
        instance.delete()

class TaskCommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs["task_id"]
        task = get_object_or_404(Task, pk=task_id)
        user = self.request.user

        if not (user == task.board.owner or user in task.board.members.all()):
            raise PermissionDenied("Zugriff verweigert.")

        return task.comments.order_by("created_at")

    def perform_create(self, serializer):
        task_id = self.kwargs["task_id"]
        task = get_object_or_404(Task, pk=task_id)
        user = self.request.user

        if not (user == task.board.owner or user in task.board.members.all()):
            raise PermissionDenied("Zugriff verweigert.")

        serializer.save(task=task, user=user)
        
class TaskCommentDeleteView(DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        task_id = self.kwargs["task_id"]
        comment_id = self.kwargs["comment_id"]
        return get_object_or_404(
            Comment,
            id=comment_id,
            task_id=task_id,
            user=self.request.user         
            )
