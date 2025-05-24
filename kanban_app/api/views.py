from django.shortcuts import render
from rest_framework import status, generics
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied

from .serializers import CommentSerializer, BoardSerializer, ColumnSerializer, TaskSerializer
from kanban_app.models import Comment, Board, Column, Task
from .permissions import IsOwnerOrReadOnly

from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

class BoardViewSet(ModelViewSet):
    serializer_class   = BoardSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(
            Q(owner=user) | Q(members=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        
def get_serializer_class(self):
    if self.action in ["retrieve", "update", "partial_update"]:
        from .serializers import BoardDetailSerializer
        return BoardDetailSerializer
    return super().get_serializer_class()

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
    serializer_class    = TaskSerializer
    permission_classes  = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(
            Q(board__owner=user) | Q(board__members=user)
        )

    def perform_create(self, serializer):
        board = serializer.validated_data['board']
        if not (board.owner == self.request.user or self.request.user in board.members.all()):
            raise PermissionDenied("Du musst Mitglied dieses Boards sein.")
        serializer.save()

    def perform_update(self, serializer):
        board = serializer.instance.board
        if not (board.owner == self.request.user or self.request.user in board.members.all()):
            raise PermissionDenied("Du musst Mitglied dieses Boards sein.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        board = instance.board
        if not (user == board.owner or user == instance.assignee):
            raise PermissionDenied("Nur der Ersteller oder Board-Owner darf löschen.")
        instance.delete()

    @action(detail=False, methods=['get'], url_path='assigned-to-me')
    def assigned_to_me(self, request):
        tasks = self.get_queryset().filter(assignee=request.user)
        return Response(self.get_serializer(tasks, many=True).data)

    @action(detail=False, methods=['get'], url_path='reviewing')
    def reviewing(self, request):
        tasks = self.get_queryset().filter(reviewer=request.user)
        return Response(self.get_serializer(tasks, many=True).data)
   
    serializer_class   = TaskSerializer
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
                
class TasksAssignedToMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(assignee=request.user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
        
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


class TaskCommentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        try:
            task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            return Response({"detail": "Task nicht gefunden."}, status=404)

        board = task.board
        user = request.user
        if not (user == board.owner or user in board.members.all()):
            return Response({"detail": "Zugriff verweigert."}, status=403)

        comments = task.comments.order_by("created_at")
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
class TaskCommentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, task_id):
        try:
            task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            return Response({"detail": "Task nicht gefunden."}, status=404)

        board = task.board
        user = request.user

        if not (user == board.owner or user in board.members.all()):
            return Response({"detail": "Zugriff verweigert."}, status=403)

        data = request.data.copy()
        data["task"] = task.id

        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
