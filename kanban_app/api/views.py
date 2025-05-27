from django.shortcuts import get_object_or_404
from django.http import Http404
from django.db.models import Q
from django.contrib.auth.models import User

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import DestroyAPIView

from .serializers import (
    BoardSummarySerializer, BoardDetailSerializer, CommentSerializer,
    BoardSerializer, ColumnSerializer, TaskSerializer
)
from kanban_app.models import Comment, Board, Column, Task
from .permissions import IsOwnerOrReadOnly

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

    def perform_update(self, serializer):
        board = self.get_object()

        if self.request.user != board.owner:
            raise PermissionDenied("Nur der Eigentümer darf Mitglieder aktualisieren.")

        members = self.request.data.get("members", None)

        instance = serializer.save()

        if members is not None:
            instance.members.set(members)

        instance.save()
        
    def perform_destroy(self, instance):
        if self.request.user != instance.owner:
            raise PermissionDenied("Nur der Eigentümer darf dieses Board löschen.")
        instance.delete()


    def get_serializer_class(self):
        if self.action == "retrieve":
            return BoardDetailSerializer
        return BoardSummarySerializer 


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
        ).distinct()

    def _check_board_access(self, board):
        user = self.request.user
        if not (board.owner == user or user in board.members.all()):
            raise PermissionDenied("Du musst Mitglied dieses Boards sein.")

    def perform_create(self, serializer):
        board = serializer.validated_data['board']
        self._check_board_access(board)
        serializer.save()

    def perform_update(self, serializer):
        board = serializer.validated_data.get("board") or serializer.instance.board
        self._check_board_access(board)
        serializer.save()


    def perform_destroy(self, instance):
        board = instance.board
        self._check_board_access(board)
        instance.delete()

    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        instance = queryset.filter(pk=kwargs["pk"]).first()
        if not instance:
            raise Http404("Task not found.")
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='assigned-to-me')
    def assigned_to_me(self, request):
        tasks = self.get_queryset().filter(assignee=request.user).distinct()
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='reviewing')
    def reviewing(self, request):
        tasks = self.get_queryset().filter(reviewer=request.user).distinct()
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='assigned-or-reviewing')
    def assigned_or_reviewing(self, request):
        tasks = self.get_queryset().filter(
            Q(assignee=request.user) | Q(reviewer=request.user)
        ).distinct()
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

class TaskCommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs["task_id"]
        task = Task.objects.filter(pk=task_id).first()
        if not task:
            raise Http404("Task not found.")

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
