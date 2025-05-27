from rest_framework import serializers
from django.db import models
from kanban_app.models import Board, Column, Task, Comment
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework.authtoken.models import Token

STATUS_CHOICES = [
    ("to-do", "To Do"),
    ("in-progress", "In Progress"),
    ("review", "Review"),
    ("done", "Done"),
]

PRIORITY_CHOICES = [
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
]

class BoardSerializer(serializers.ModelSerializer):
    owner_id = serializers.ReadOnlyField(source='owner.id')
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all()
    )
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'description',
            'owner_id',
            'members',
            'member_count',
            'ticket_count',
            'tasks_to_do_count',
            'tasks_high_prio_count',
        ]

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority="high").count()
        
class ColumnSerializer(serializers.ModelSerializer):
    position = serializers.IntegerField(source="order")
    board    = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all())

    class Meta:
        model  = Column
        fields = [
            "id",
            "title",
            "position",  
            "board",
        ]
        
class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    task = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'task', 'user', 'content', 'created_at']
   
class SimpleUserSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

    def get_fullname(self, obj):
        return obj.get_full_name()     

class TaskSerializer(serializers.ModelSerializer):
    board = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all(), required=True)
    status = serializers.ChoiceField(choices=STATUS_CHOICES)
    priority = serializers.ChoiceField(choices=PRIORITY_CHOICES)
    assignee = SimpleUserSerializer(read_only=True)
    reviewer = SimpleUserSerializer(read_only=True)

    assignee_id = serializers.PrimaryKeyRelatedField(
        source='assignee',
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source='reviewer',
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )

    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'status', 'title', 'description',
            'priority', 'assignee', 'reviewer',
            'assignee_id', 'reviewer_id', 'due_date', 'comments_count'
        ]

    def get_comments_count(self, obj):
        return obj.comments.count()

    def validate(self, data):
        board = data.get("board")
        assignee = data.get("assignee")
        reviewer = data.get("reviewer")

        if not board:
            raise serializers.ValidationError({"board": "Board is required and must be provided."})

        if assignee and assignee not in board.members.all() and assignee != board.owner:
            raise serializers.ValidationError("Assignee must be a board member or owner.")

        if reviewer and reviewer not in board.members.all() and reviewer != board.owner:
            raise serializers.ValidationError("Reviewer must be a board member or owner.")

        return data
  
class BoardDetailSerializer(BoardSerializer):
    owner_data = SimpleUserSerializer(source="owner", read_only=True)
    members_data = SimpleUserSerializer(source="members", many=True, read_only=True)
    tasks = serializers.SerializerMethodField()

    class Meta(BoardSerializer.Meta):
        fields = BoardSerializer.Meta.fields + ["owner_data", "members_data", "tasks"]

    def get_tasks(self, obj):
        return TaskSerializer(obj.tasks.all(), many=True).data

