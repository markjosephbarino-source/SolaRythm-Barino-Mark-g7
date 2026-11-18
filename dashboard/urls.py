from django.urls import path

from .views import AdminDashboardView, DashboardRedirectView, MemberDashboardView

urlpatterns = [
    path("", DashboardRedirectView.as_view(), name="dashboard"),
    path("dashboard/admin/", AdminDashboardView.as_view(), name="admin_dashboard"),
    path("dashboard/member/", MemberDashboardView.as_view(), name="member_dashboard"),
]
