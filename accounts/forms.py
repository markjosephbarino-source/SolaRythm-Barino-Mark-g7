import re

from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser

PHONE_PATTERN = re.compile(r"^\+?[0-9][0-9\s\-]{6,18}$")
MAX_PHOTO_MB = 2


class CustomUserCreationForm(UserCreationForm):
    """Registration form. `role` is NOT a field, so users cannot make themselves Admin."""

    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "email", "first_name", "last_name", "contact_number")

    def clean_username(self):
        username = self.cleaned_data["username"]
        if CustomUser.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_contact_number(self):
        return _validate_phone(self.cleaned_data.get("contact_number", ""))


class ProfileUpdateForm(forms.ModelForm):
    """Edit own profile. Role, username and password are not editable here."""

    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "email", "contact_number", "profile_photo")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["email"].required = True

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        taken = CustomUser.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if taken.exists():
            raise forms.ValidationError("Another account already uses this email.")
        return email

    def clean_contact_number(self):
        return _validate_phone(self.cleaned_data.get("contact_number", ""))

    def clean_profile_photo(self):
        photo = self.cleaned_data.get("profile_photo")
        if photo and hasattr(photo, "size") and photo.size > MAX_PHOTO_MB * 1024 * 1024:
            raise forms.ValidationError(f"Photo must be {MAX_PHOTO_MB} MB or smaller.")
        return photo


def _validate_phone(value):
    value = (value or "").strip()
    if value and not PHONE_PATTERN.match(value):
        raise forms.ValidationError("Enter a valid contact number (digits, spaces, dashes, optional +).")
    return value
