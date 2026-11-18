from django.urls import path

from .views import (ProfileUpdateView, ProfileView, SignUpView,
                    SolaLoginView, SolaLogoutView)

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", SolaLoginView.as_view(), name="login"),
    path("logout/", SolaLogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/edit/", ProfileUpdateView.as_view(), name="profile_edit"),
]
