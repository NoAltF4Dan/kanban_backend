from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from kanban_app.models import Board

class TestBoardPermissions(APITestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(username="user_a", password="pass1234")
        self.user_b = User.objects.create_user(username="user_b", password="pass1234")

        self.client.force_authenticate(user=self.user_a)
        response = self.client.post("/api/boards/", {
            "title": "User A Board",
            "description": "Private content"
        })
        self.board_id = response.data["id"]

    def test_user_b_cannot_see_user_a_board(self):
        self.client.force_authenticate(user=self.user_b)

        response = self.client.get(f"/api/boards/{self.board_id}/")

        self.assertIn(response.status_code, [403, 404])
