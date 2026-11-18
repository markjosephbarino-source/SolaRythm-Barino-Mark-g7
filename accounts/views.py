from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView

from .forms import CustomUserCreationForm, ProfileUpdateForm


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Account created successfully! You can now log in.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Registration failed. Please fix the errors below.")
        return super().form_invalid(form)


class SolaLoginView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, f"Welcome back, {form.get_user().first_name or form.get_user().username}!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password. Please try again.")
        return super().form_invalid(form)


class SolaLogoutView(LogoutView):
    """Django 5+ requires logout via POST (the nav button already does this)."""

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        messages.info(request, "You have been logged out.")
        return response


class ProfileView(LoginRequiredMixin, TemplateView):
    """Shows ONLY the logged-in user's own profile (no user id in the URL)."""

    template_name = "accounts/profile.html"


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = ProfileUpdateForm
    template_name = "accounts/profile_edit.html"
    success_url = reverse_lazy("profile")

    def get_object(self, queryset=None):
        return self.request.user  # users can only edit themselves

    def form_valid(self, form):
        messages.success(self.request, "Your profile was updated.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Could not update your profile. Please fix the errors below.")
        return super().form_invalid(form)
