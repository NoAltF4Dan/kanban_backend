from rest_framework import serializers
from django.db import models
from kanban_app.models import Board, Column, Task, Comment
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework.authtoken.models import Token

class BoardSerializer(serializers.ModelSerializer):
    owner_id = serializers.ReadOnlyField(source='owner.id')
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all()
    )
    member_count          = serializers.SerializerMethodField()
    ticket_count          = serializers.SerializerMethodField()
    tasks_to_do_count     = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model  = Board
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
        total = 0
        for column in obj.columns.all():
            total += column.tasks.count()
        return total

    def get_tasks_to_do_count(self, obj):
        total = 0
        for column in obj.columns.all():
            total += column.tasks.filter(status='todo').count()
        return total

    def get_tasks_high_prio_count(self, obj):
        total = 0
        for column in obj.columns.all():
            total += column.tasks.filter(priority='high').count()
        return total
     
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
    board = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all(), read_only=True)
    column = serializers.PrimaryKeyRelatedField(queryset=Column.objects.all())

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
            'id', 'board', 'column', 'title', 'description',
            'status', 'priority',
            'assignee', 'reviewer', 'assignee_id', 'reviewer_id',
            'due_date', 'comments_count'
        ]

    def get_comments_count(self, obj):
        return obj.comments.count()

    def validate(self, data):
        board = data.get("board")
        assignee = data.get("assignee")
        reviewer = data.get("reviewer")
        user = self.context.get("request").user

        if assignee and assignee not in board.members.all() and assignee != board.owner:
            raise serializers.ValidationError("Assignee muss Mitglied des Boards sein.")

        if reviewer and reviewer not in board.members.all() and reviewer != board.owner:
            raise serializers.ValidationError("Reviewer muss Mitglied des Boards sein.")
        return data

    
class BoardDetailSerializer(BoardSerializer):
    members_data = SimpleUserSerializer(source="members", many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)
    owner_data = SimpleUserSerializer(source="owner", read_only=True)

    class Meta(BoardSerializer.Meta):
        fields = BoardSerializer.Meta.fields + ["owner_data", "members_data", "tasks"]

