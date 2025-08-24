from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Company, FinancialSummary, LobbyingReport, PoliticalContribution, CharitableGrant
from .serializers import (
    CompanySerializer, CompanyDetailSerializer,
    FinancialSummarySerializer, LobbyingReportSerializer,
    PoliticalContributionSerializer, CharitableGrantSerializer
)


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CompanyDetailSerializer
        return CompanySerializer
    
    @action(detail=True, methods=['get'])
    def spending_summary(self, request, pk=None):
        """Get a summary of all spending for a company."""
        company = self.get_object()
        
        # Calculate totals
        total_lobbying = sum(report.amount_spent for report in company.lobbying_reports.all())
        total_charitable = sum(grant.amount for grant in company.charitable_grants.all())
        
        # Get political contributions for this company's PACs
        pac_contributions = PoliticalContribution.objects.filter(
            company_pac_id__icontains=company.name.split()[0]  # Simple matching
        )
        total_political = sum(contribution.amount for contribution in pac_contributions)
        
        return Response({
            'company_name': company.name,
            'total_lobbying': total_lobbying,
            'total_charitable': total_charitable,
            'total_political': total_political,
            'total_spending': total_lobbying + total_charitable + total_political
        })


class FinancialSummaryViewSet(viewsets.ModelViewSet):
    queryset = FinancialSummary.objects.all()
    serializer_class = FinancialSummarySerializer


class LobbyingReportViewSet(viewsets.ModelViewSet):
    queryset = LobbyingReport.objects.all()
    serializer_class = LobbyingReportSerializer


class PoliticalContributionViewSet(viewsets.ModelViewSet):
    queryset = PoliticalContribution.objects.all()
    serializer_class = PoliticalContributionSerializer


class CharitableGrantViewSet(viewsets.ModelViewSet):
    queryset = CharitableGrant.objects.all()
    serializer_class = CharitableGrantSerializer
