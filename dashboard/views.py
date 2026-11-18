from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView

from accounts.models import CustomUser


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Logged-out -> login page. Wrong role -> 403 Forbidden."""

    required_role = None

    def test_func(self):
        return self.request.user.role == self.required_role


class DashboardRedirectView(LoginRequiredMixin, View):
    """Landing point after login: send each user to the dashboard for their role."""

    def get(self, request, *args, **kwargs):
        if request.user.role == CustomUser.Role.ADMIN:
            return redirect("admin_dashboard")
        return redirect("member_dashboard")


class AdminDashboardView(RoleRequiredMixin, TemplateView):
    template_name = "dashboard/admin_dashboard.html"
    required_role = CustomUser.Role.ADMIN

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users = CustomUser.objects
        context["total_users"] = users.count()
        context["admin_count"] = users.filter(role=CustomUser.Role.ADMIN).count()
        context["member_count"] = users.filter(role=CustomUser.Role.MEMBER).count()
        context["recent_users"] = users.order_by("-date_joined")[:8]
        return context


class MemberDashboardView(RoleRequiredMixin, TemplateView):
    template_name = "dashboard/member_dashboard.html"
    required_role = CustomUser.Role.MEMBER
