from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import UserProfile
from dashboard.models import AIAnalysisLog


class DashboardTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="SecurePassword123!",
        )

        UserProfile.objects.create(
            user=self.user,
            full_name="Test User",
            age=22,
        )

    def test_dashboard_redirects_anonymous_user_to_login(self):
        response = self.client.get(reverse("dashboard:home"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse("accounts:login"),
            response.url,
        )

    def test_logged_in_user_can_open_dashboard(self):
        self.client.login(
            username="test@example.com",
            password="SecurePassword123!",
        )

        response = self.client.get(reverse("dashboard:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome, Test User")

    def test_recent_activity_is_displayed(self):
        AIAnalysisLog.objects.create(
            user=self.user,
            activity_type="STOCK_SEARCH",
            title="Searched RELIANCE",
            description="Educational stock search activity.",
        )

        self.client.login(
            username="test@example.com",
            password="SecurePassword123!",
        )

        response = self.client.get(reverse("dashboard:home"))

        self.assertContains(response, "Searched RELIANCE")