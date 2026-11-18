import io

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from .models import CustomUser

GOOD = "Sunny!Day#2026"


def make_user(username="maria", email="maria@example.com", role=CustomUser.Role.MEMBER, password=GOOD):
    return CustomUser.objects.create_user(
        username=username, email=email, password=password,
        first_name="Maria", last_name="Santos", role=role)


class RegistrationTests(TestCase):
    def payload(self, **over):
        data = {"username": "newuser", "email": "new@example.com", "first_name": "New",
                "last_name": "User", "contact_number": "0917 123 4567",
                "password1": GOOD, "password2": GOOD}
        data.update(over)
        return data

    def test_register_success_hashes_password_and_defaults_to_member(self):
        r = self.client.post(reverse("signup"), self.payload(), follow=True)
        self.assertRedirects(r, reverse("login"))
        self.assertContains(r, "Account created successfully")
        u = CustomUser.objects.get(username="newuser")
        self.assertEqual(u.role, CustomUser.Role.MEMBER)
        self.assertNotEqual(u.password, GOOD)
        self.assertTrue(u.password.startswith(("pbkdf2_", "argon2", "bcrypt", "scrypt")))
        self.assertTrue(u.check_password(GOOD))

    def test_cannot_self_promote_to_admin(self):
        self.client.post(reverse("signup"), self.payload(role="ADMIN", is_staff="on", is_superuser="on"))
        u = CustomUser.objects.get(username="newuser")
        self.assertEqual(u.role, CustomUser.Role.MEMBER)
        self.assertFalse(u.is_staff or u.is_superuser)

    def test_password_mismatch(self):
        r = self.client.post(reverse("signup"), self.payload(password2="different"))
        self.assertEqual(CustomUser.objects.count(), 0)
        self.assertContains(r, "Registration failed")

    def test_invalid_email(self):
        r = self.client.post(reverse("signup"), self.payload(email="not-an-email"))
        self.assertEqual(CustomUser.objects.count(), 0)
        self.assertContains(r, "valid email")

    def test_required_fields(self):
        r = self.client.post(reverse("signup"), {})
        self.assertEqual(CustomUser.objects.count(), 0)
        self.assertContains(r, "This field is required")

    def test_duplicate_username_case_insensitive(self):
        make_user(username="Maria")
        r = self.client.post(reverse("signup"), self.payload(username="maria"))
        self.assertContains(r, "already taken")

    def test_duplicate_email_case_insensitive(self):
        make_user(email="maria@example.com")
        r = self.client.post(reverse("signup"), self.payload(email="MARIA@example.com"))
        self.assertContains(r, "already exists")
        self.assertEqual(CustomUser.objects.count(), 1)

    def test_weak_password_rejected(self):
        self.client.post(reverse("signup"), self.payload(password1="12345678", password2="12345678"))
        self.assertEqual(CustomUser.objects.count(), 0)

    def test_bad_phone_rejected(self):
        r = self.client.post(reverse("signup"), self.payload(contact_number="abc"))
        self.assertContains(r, "valid contact number")


class LoginLogoutTests(TestCase):
    def test_member_login_goes_to_member_dashboard(self):
        make_user()
        r = self.client.post(reverse("login"), {"username": "maria", "password": GOOD}, follow=True)
        self.assertRedirects(r, reverse("member_dashboard"))

    def test_admin_login_goes_to_admin_dashboard(self):
        make_user("boss", "boss@example.com", CustomUser.Role.ADMIN)
        r = self.client.post(reverse("login"), {"username": "boss", "password": GOOD}, follow=True)
        self.assertRedirects(r, reverse("admin_dashboard"))

    def test_invalid_credentials_show_error(self):
        make_user()
        r = self.client.post(reverse("login"), {"username": "maria", "password": "wrong"})
        self.assertContains(r, "Invalid username or password")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_ends_session(self):
        make_user()
        self.client.login(username="maria", password=GOOD)
        r = self.client.post(reverse("logout"), follow=True)
        self.assertRedirects(r, reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)
        r = self.client.get(reverse("member_dashboard"))
        self.assertEqual(r.status_code, 302)

    def test_logout_requires_post(self):
        make_user()
        self.client.login(username="maria", password=GOOD)
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)

    def test_superuser_gets_admin_role(self):
        u = CustomUser.objects.create_superuser("root", "root@example.com", GOOD)
        self.assertEqual(u.role, CustomUser.Role.ADMIN)


class ProfileTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.other = make_user("juan", "juan@example.com")

    def test_profile_requires_login(self):
        for name in ("profile", "profile_edit"):
            r = self.client.get(reverse(name))
            self.assertRedirects(r, f"{reverse('login')}?next={reverse(name)}")

    def test_view_own_profile(self):
        self.client.login(username="maria", password=GOOD)
        r = self.client.get(reverse("profile"))
        self.assertContains(r, "maria@example.com")
        self.assertNotContains(r, "juan@example.com")

    def test_update_own_profile(self):
        self.client.login(username="maria", password=GOOD)
        r = self.client.post(reverse("profile_edit"), {
            "first_name": "Mariah", "last_name": "Santos",
            "email": "mariah@example.com", "contact_number": "+63 917 000 1111"}, follow=True)
        self.assertRedirects(r, reverse("profile"))
        self.assertContains(r, "Your profile was updated")
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Mariah")
        self.assertEqual(self.user.email, "mariah@example.com")

    def test_cannot_edit_other_user_or_role(self):
        self.client.login(username="maria", password=GOOD)
        self.client.post(reverse("profile_edit"), {
            "first_name": "Hacked", "last_name": "X", "email": "maria@example.com",
            "role": "ADMIN", "username": "juan", "id": self.other.pk})
        self.user.refresh_from_db(); self.other.refresh_from_db()
        self.assertEqual(self.user.role, CustomUser.Role.MEMBER)
        self.assertEqual(self.other.first_name, "Maria")
        self.assertEqual(self.user.username, "maria")

    def test_duplicate_email_on_update(self):
        self.client.login(username="maria", password=GOOD)
        r = self.client.post(reverse("profile_edit"), {
            "first_name": "Maria", "last_name": "Santos", "email": "juan@example.com"})
        self.assertContains(r, "already uses this email")

    def test_photo_upload(self):
        self.client.login(username="maria", password=GOOD)
        buf = io.BytesIO(); Image.new("RGB", (20, 20), "orange").save(buf, "PNG")
        photo = SimpleUploadedFile("me.png", buf.getvalue(), content_type="image/png")
        with self.settings(MEDIA_ROOT="/tmp/solarythm_test_media"):
            r = self.client.post(reverse("profile_edit"), {
                "first_name": "Maria", "last_name": "Santos",
                "email": "maria@example.com", "profile_photo": photo}, follow=True)
        self.assertRedirects(r, reverse("profile"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.profile_photo.name.startswith("profile_photos/"))
