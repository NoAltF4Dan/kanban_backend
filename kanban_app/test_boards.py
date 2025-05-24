from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from kanban_app.models import Board

class TestBoardAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="testpass123")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_create_board(self):
        response = self.client.post("/api/boards/", {
            "title": "Meine erste Test-Board",
            "description": "Testbeschreibung"
        })
            
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Board.objects.count(), 1)

