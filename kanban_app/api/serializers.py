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

class SimpleUserSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

    def get_fullname(self, obj):
        return obj.get_full_name()

class BoardSerializer(serializers.ModelSerializer):
    owner_id = serializers.ReadOnlyField(source='owner.id')
    members = SimpleUserSerializer(many=True, read_only=True)
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            'id', 'title', 'description',
            'owner_id', 'members',
            'member_count', 'ticket_count',
            'tasks_to_do_count', 'tasks_high_prio_count'
        ]

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority='high').count()
    
class BoardDetailSerializer(serializers.ModelSerializer):
    owner_id = serializers.ReadOnlyField(source='owner.id')
    members = SimpleUserSerializer(many=True, read_only=True)
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'owner_id',
            'members',
            'tasks'
        ]

    def get_tasks(self, obj):
        return TaskSerializer(obj.tasks.all(), many=True).data

class BoardSummarySerializer(serializers.ModelSerializer):
        owner_id = serializers.ReadOnlyField(source='owner.id')
        member_count = serializers.SerializerMethodField()
        ticket_count = serializers.SerializerMethodField()
        tasks_to_do_count = serializers.SerializerMethodField()
        tasks_high_prio_count = serializers.SerializerMethodField()

        class Meta:
            model = Board
            fields = [
                'id',
                'title',
                'owner_id',
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
            return obj.tasks.filter(status='to-do').count()

        def get_tasks_high_prio_count(self, obj):
            return obj.tasks.filter(priority='high').count()

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
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']
        read_only_fields = ['id', 'created_at', 'author']

    def get_author(self, obj):
        return SimpleUserSerializer(obj.user).data if obj.user else None

class SimpleUserSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

    def get_fullname(self, obj):
        return obj.get_full_name()
    
class TaskSerializer(serializers.ModelSerializer):
    assignee = serializers.SerializerMethodField()
    reviewer = serializers.SerializerMethodField()
    board = serializers.PrimaryKeyRelatedField(
        queryset=Board.objects.all(),
        write_only=True
    )
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, required=False, allow_null=True, source='assignee'
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, required=False, allow_null=True, source='reviewer'
    )

    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status',
            'priority', 'assignee', 'reviewer',
            'assignee_id', 'reviewer_id',
            'due_date', 'comments_count'
        ]
        read_only_fields = ['id', 'comments_count']

    def get_assignee(self, obj):
        return SimpleUserSerializer(obj.assignee).data if obj.assignee else None

    def get_reviewer(self, obj):
        return SimpleUserSerializer(obj.reviewer).data if obj.reviewer else None

    def get_comments_count(self, obj):
        return obj.comments.count()

    def validate(self, data):
        board = data.get("board") or getattr(self.instance, "board", None)
        assignee = data.get("assignee") or getattr(self.instance, "assignee", None)
        reviewer = data.get("reviewer") or getattr(self.instance, "reviewer", None)

        if not board:
            raise serializers.ValidationError({"board": "Board is required for validation."})

        if assignee and assignee not in board.members.all() and assignee != board.owner:
            raise serializers.ValidationError({"assignee": "Assignee must be a board member or the owner."})

        if reviewer and reviewer not in board.members.all() and reviewer != board.owner:
            raise serializers.ValidationError({"reviewer": "Reviewer must be a board member or the owner."})

        return data

  
class BoardDetailSerializer(serializers.ModelSerializer):
    owner_id = serializers.ReadOnlyField(source="owner.id")
    members = SimpleUserSerializer(many=True, read_only=True)
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "owner_id",
            "members",
            "tasks"
        ]

    def get_tasks(self, obj):
        return TaskSerializer(obj.tasks.all(), many=True).data