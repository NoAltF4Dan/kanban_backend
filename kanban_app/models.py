from django.db import models
from django.contrib.auth.models import User


STATUS_CHOICES = [
    ("todo", "To Do"),
    ("in_progress", "In Progress"),
    ("review", "Review"),
    ("done", "Done"),
]

PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]


class Board(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="boards")
    members = models.ManyToManyField(User, related_name="shared_boards", blank=True)
    
    class Meta:
        ordering = ['-created_at']  
        verbose_name = "Board"
        verbose_name_plural = "Boards"
    
    def __str__(self):
        return self.title
    
    
class Column(models.Model):
    title = models.CharField(max_length=50)
    order = models.PositiveIntegerField()
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="columns")

    class Meta:
        ordering = ['order']
        verbose_name = "Column"
        verbose_name_plural = "Columns"
    
    def __str__(self):
        return f"{self.title} (Board: {self.board.title})"
    
    
class Task(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="to-do")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium")
    assignee = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_tasks")
    reviewer = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="review_tasks")
    due_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['due_date']
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def __str__(self):
        return f"{self.title} ({self.status})"
    
    
class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
