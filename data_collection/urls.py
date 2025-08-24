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
]
