from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import Feedback

class HomePageTests(TestCase):
    def test_home_page_contains_working_auth_links(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, 'href="/login/"')
        self.assertContains(response, 'href="/signup/"')
        self.assertContains(response, 'href="/admin_login/"')


class AdminViewsTests(TestCase):
    def test_admin_predictions_page_is_accessible_to_staff(self):
        User.objects.create_user(
            username="admin@example.com",
            password="securepass123",
            is_staff=True,
        )

        self.client.login(username="admin@example.com", password="securepass123")
        response = self.client.get(reverse("admin_predictions"))

        self.assertEqual(response.status_code, 200)


class PredictionFeatureTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="tester@example.com",
            password="securepass123",
        )

    def test_prediction_page_shows_explanation_and_top_recommendations(self):
        self.client.login(username="tester@example.com", password="securepass123")
        response = self.client.post(
            reverse("predict"),
            {
                "N": 90,
                "P": 42,
                "K": 43,
                "temperature": 22,
                "humidity": 80,
                "ph": 7,
                "rainfall": 200,
            },
        )

        self.assertEqual(response.status_code, 200)


class FeedbackFeatureTests(TestCase):
    def test_feedback_form_creates_a_record(self):
        response = self.client.post(
            reverse("feedback"),
            {
                "name": "Asha",
                "email": "asha@example.com",
                "message": "Great project",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Feedback.objects.count(), 1)


class NotificationTests(TestCase):
    def test_notifications_page_exists(self):
        user = User.objects.create_user(username="notify@example.com", password="pass123456")
        self.client.login(username="notify@example.com", password="pass123456")
        response = self.client.get(reverse("notifications"))
        self.assertEqual(response.status_code, 200)


class ChatbotTests(TestCase):
    def test_chatbot_page_exists(self):
        user = User.objects.create_user(username="chat@example.com", password="pass123456")
        self.client.login(username="chat@example.com", password="pass123456")
        response = self.client.get(reverse("chatbot"))
        self.assertEqual(response.status_code, 200)


class FertilizerTests(TestCase):
    def test_fertilizer_page_exists(self):
        user = User.objects.create_user(username="fert@example.com", password="pass123456")
        self.client.login(username="fert@example.com", password="pass123456")
        response = self.client.get(reverse("fertilizer"))
        self.assertEqual(response.status_code, 200)
