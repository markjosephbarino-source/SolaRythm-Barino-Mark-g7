from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser

PW = "Sunny!Day#2026"


class RoleAccessTests(TestCase):
    def setUp(self):
        self.member = CustomUser.objects.create_user("maria", "m@example.com", PW)
        self.admin = CustomUser.objects.create_user("boss", "b@example.com", PW, role=CustomUser.Role.ADMIN)

    def test_logged_out_redirected_to_login(self):
        for name in ("dashboard", "member_dashboard", "admin_dashboard"):
            r = self.client.get(reverse(name))
            self.assertRedirects(r, f"{reverse('login')}?next={reverse(name)}")

    def test_member_blocked_from_admin_dashboard(self):
        self.client.login(username="maria", password=PW)
        self.assertEqual(self.client.get(reverse("admin_dashboard")).status_code, 403)
        self.assertEqual(self.client.get(reverse("member_dashboard")).status_code, 200)

    def test_admin_blocked_from_member_dashboard(self):
        self.client.login(username="boss", password=PW)
        self.assertEqual(self.client.get(reverse("member_dashboard")).status_code, 403)
        r = self.client.get(reverse("admin_dashboard"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Total users")

    def test_root_redirects_by_role(self):
        self.client.login(username="maria", password=PW)
        self.assertRedirects(self.client.get(reverse("dashboard")), reverse("member_dashboard"))
        self.client.logout(); self.client.login(username="boss", password=PW)
        self.assertRedirects(self.client.get(reverse("dashboard")), reverse("admin_dashboard"))

    def test_nav_matches_role(self):
        self.client.login(username="maria", password=PW)
        r = self.client.get(reverse("member_dashboard"))
        self.assertNotContains(r, "Admin Dashboard")
