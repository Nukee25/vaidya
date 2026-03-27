from django.urls import path

from .views import HealthScoreView, LoginView, PredictView, ReportDetailView, ReportsView, SignupView

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("predict/", PredictView.as_view(), name="predict"),
    path("reports/", ReportsView.as_view(), name="reports"),
    path("health-score/", HealthScoreView.as_view(), name="health-score"),
    path("reports/<int:report_id>/", ReportDetailView.as_view(), name="report-detail"),
]
