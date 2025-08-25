from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'companies', views.CompanyViewSet)
router.register(r'financial-summaries', views.FinancialSummaryViewSet)
router.register(r'lobbying-reports', views.LobbyingReportViewSet)
router.register(r'political-contributions', views.PoliticalContributionViewSet)
router.register(r'charitable-grants', views.CharitableGrantViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/logs/', views.log_frontend, name='log-frontend'),
    path('api/logs/get/', views.get_logs, name='get-logs'),
    path('api/analytics/dashboard/', views.dashboard_summary, name='dashboard-summary'),
    path('api/analytics/spending_comparison/', views.spending_comparison, name='spending-comparison'),
]
