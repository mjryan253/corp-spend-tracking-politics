from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import Company, FinancialSummary, LobbyingReport, PoliticalContribution, CharitableGrant
from .serializers import (
    CompanySerializer, CompanyDetailSerializer, FinancialSummarySerializer,
    LobbyingReportSerializer, PoliticalContributionSerializer, CharitableGrantSerializer
)


class CompanyViewSet(viewsets.ModelViewSet):
    """API endpoint for companies with advanced filtering and search."""
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['ticker', 'cik', 'headquarters_location']
    search_fields = ['name', 'ticker', 'cik']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CompanyDetailSerializer
        return CompanySerializer

    @action(detail=True, methods=['get'])
    def spending_summary(self, request, pk=None):
        """Get comprehensive spending summary for a company."""
        company = self.get_object()
        
        # Get date range from query params
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Base querysets
        lobbying_qs = company.lobbying_reports.all()
        charitable_qs = company.charitable_grants.all()
        political_qs = PoliticalContribution.objects.filter(
            company_pac_id__icontains=company.name.split()[0]
        )
        
        # Apply date filters if provided
        if start_date:
            lobbying_qs = lobbying_qs.filter(year__gte=int(start_date))
            charitable_qs = charitable_qs.filter(fiscal_year__gte=int(start_date))
            political_qs = political_qs.filter(date__gte=start_date)
        
        if end_date:
            lobbying_qs = lobbying_qs.filter(year__lte=int(end_date))
            charitable_qs = charitable_qs.filter(fiscal_year__lte=int(end_date))
            political_qs = political_qs.filter(date__lte=end_date)
        
        # Calculate totals
        lobbying_total = lobbying_qs.aggregate(total=Sum('amount_spent'))['total'] or Decimal('0')
        charitable_total = charitable_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        political_total = political_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Get category breakdown for charitable grants
        charitable_by_category = charitable_qs.values('recipient_category').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
        
        # Get recent financial data
        latest_financial = company.financial_summaries.order_by('-fiscal_year').first()
        
        return Response({
            'company': {
                'id': company.id,
                'name': company.name,
                'ticker': company.ticker,
                'cik': company.cik,
            },
            'spending_totals': {
                'lobbying': float(lobbying_total),
                'charitable': float(charitable_total),
                'political': float(political_total),
                'total': float(lobbying_total + charitable_total + political_total),
            },
            'charitable_breakdown': list(charitable_by_category),
            'financial_context': {
                'latest_revenue': float(latest_financial.total_revenue) if latest_financial else None,
                'latest_net_income': float(latest_financial.net_income) if latest_financial else None,
                'fiscal_year': latest_financial.fiscal_year if latest_financial else None,
            },
            'record_counts': {
                'lobbying_reports': lobbying_qs.count(),
                'charitable_grants': charitable_qs.count(),
                'political_contributions': political_qs.count(),
            }
        })

    @action(detail=False, methods=['get'])
    def top_spenders(self, request):
        """Get top spending companies across all categories."""
        limit = int(request.query_params.get('limit', 10))
        category = request.query_params.get('category', 'all')  # all, lobbying, charitable, political
        
        companies = Company.objects.all()
        results = []
        
        for company in companies:
            # Calculate spending based on category
            if category == 'lobbying' or category == 'all':
                lobbying_total = company.lobbying_reports.aggregate(
                    total=Sum('amount_spent')
                )['total'] or Decimal('0')
            else:
                lobbying_total = Decimal('0')
                
            if category == 'charitable' or category == 'all':
                charitable_total = company.charitable_grants.aggregate(
                    total=Sum('amount')
                )['total'] or Decimal('0')
            else:
                charitable_total = Decimal('0')
                
            if category == 'political' or category == 'all':
                political_total = PoliticalContribution.objects.filter(
                    company_pac_id__icontains=company.name.split()[0]
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            else:
                political_total = Decimal('0')
            
            total_spending = lobbying_total + charitable_total + political_total
            
            if total_spending > 0:
                results.append({
                    'company': {
                        'id': company.id,
                        'name': company.name,
                        'ticker': company.ticker,
                    },
                    'spending': {
                        'lobbying': float(lobbying_total),
                        'charitable': float(charitable_total),
                        'political': float(political_total),
                        'total': float(total_spending),
                    }
                })
        
        # Sort by total spending and limit results
        results.sort(key=lambda x: x['spending']['total'], reverse=True)
        return Response(results[:limit])

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Advanced search with multiple criteria."""
        query = request.query_params.get('q', '')
        min_spending = request.query_params.get('min_spending')
        max_spending = request.query_params.get('max_spending')
        has_lobbying = request.query_params.get('has_lobbying')
        has_charitable = request.query_params.get('has_charitable')
        has_political = request.query_params.get('has_political')
        
        queryset = Company.objects.all()
        
        # Text search
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(ticker__icontains=query) |
                Q(cik__icontains=query)
            )
        
        # Filter by spending criteria
        if min_spending or max_spending:
            companies_with_spending = []
            for company in queryset:
                total_spending = self._calculate_company_spending(company)
                
                if min_spending and total_spending < Decimal(min_spending):
                    continue
                if max_spending and total_spending > Decimal(max_spending):
                    continue
                    
                companies_with_spending.append(company.id)
            
            queryset = queryset.filter(id__in=companies_with_spending)
        
        # Filter by data availability
        if has_lobbying == 'true':
            queryset = queryset.filter(lobbying_reports__isnull=False).distinct()
        if has_charitable == 'true':
            queryset = queryset.filter(charitable_grants__isnull=False).distinct()
        if has_political == 'true':
            # This is a simplified check - in practice you'd need a more sophisticated approach
            pass
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def _calculate_company_spending(self, company):
        """Calculate total spending for a company."""
        lobbying_total = company.lobbying_reports.aggregate(
            total=Sum('amount_spent')
        )['total'] or Decimal('0')
        
        charitable_total = company.charitable_grants.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        
        political_total = PoliticalContribution.objects.filter(
            company_pac_id__icontains=company.name.split()[0]
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        return lobbying_total + charitable_total + political_total


class FinancialSummaryViewSet(viewsets.ModelViewSet):
    """API endpoint for financial summaries."""
    queryset = FinancialSummary.objects.all()
    serializer_class = FinancialSummarySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['company', 'fiscal_year']
    search_fields = ['company__name', 'company__ticker']
    ordering_fields = ['fiscal_year', 'total_revenue', 'net_income']
    ordering = ['-fiscal_year']

    @action(detail=False, methods=['get'])
    def financial_ratios(self, request):
        """Calculate financial ratios for companies."""
        company_id = request.query_params.get('company')
        year = request.query_params.get('year')
        
        queryset = self.get_queryset()
        
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        if year:
            queryset = queryset.filter(fiscal_year=year)
        
        results = []
        for financial in queryset:
            if financial.total_revenue and financial.total_revenue > 0:
                profit_margin = (financial.net_income / financial.total_revenue) * 100
            else:
                profit_margin = 0
            
            results.append({
                'company': financial.company.name,
                'fiscal_year': financial.fiscal_year,
                'revenue': float(financial.total_revenue) if financial.total_revenue else 0,
                'net_income': float(financial.net_income) if financial.net_income else 0,
                'profit_margin_percent': float(profit_margin),
            })
        
        return Response(results)


class LobbyingReportViewSet(viewsets.ModelViewSet):
    """API endpoint for lobbying reports."""
    queryset = LobbyingReport.objects.all()
    serializer_class = LobbyingReportSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['company', 'year', 'quarter']
    search_fields = ['company__name', 'specific_issues']
    ordering_fields = ['year', 'quarter', 'amount_spent', 'created_at']
    ordering = ['-year', '-quarter']

    @action(detail=False, methods=['get'])
    def spending_trends(self, request):
        """Get lobbying spending trends over time."""
        company_id = request.query_params.get('company')
        start_year = request.query_params.get('start_year', 2020)
        end_year = request.query_params.get('end_year', timezone.now().year)
        
        queryset = self.get_queryset().filter(
            year__gte=start_year,
            year__lte=end_year
        )
        
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        # Group by year and quarter
        trends = queryset.values('year', 'quarter').annotate(
            total_spent=Sum('amount_spent'),
            report_count=Count('id')
        ).order_by('year', 'quarter')
        
        return Response(list(trends))

    @action(detail=False, methods=['get'])
    def top_issues(self, request):
        """Get most lobbied issues."""
        limit = int(request.query_params.get('limit', 10))
        
        # This is a simplified approach - in practice you'd want to parse the specific_issues field
        # and count individual issues
        queryset = self.get_queryset()
        
        # For now, return companies with highest lobbying spending
        top_lobbyists = queryset.values('company__name').annotate(
            total_spent=Sum('amount_spent'),
            report_count=Count('id')
        ).order_by('-total_spent')[:limit]
        
        return Response(list(top_lobbyists))


class PoliticalContributionViewSet(viewsets.ModelViewSet):
    """API endpoint for political contributions."""
    queryset = PoliticalContribution.objects.all()
    serializer_class = PoliticalContributionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['election_cycle', 'recipient_party']
    search_fields = ['company_pac_id', 'recipient_name']
    ordering_fields = ['date', 'amount', 'election_cycle']
    ordering = ['-date']

    @action(detail=False, methods=['get'])
    def contribution_trends(self, request):
        """Get political contribution trends."""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        election_cycle = request.query_params.get('election_cycle')
        
        queryset = self.get_queryset()
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        if election_cycle:
            queryset = queryset.filter(election_cycle=election_cycle)
        
        # Group by month
        trends = queryset.extra(
            select={'month': "DATE_TRUNC('month', date)"}
        ).values('month').annotate(
            total_amount=Sum('amount'),
            contribution_count=Count('id')
        ).order_by('month')
        
        return Response(list(trends))

    @action(detail=False, methods=['get'])
    def party_breakdown(self, request):
        """Get political contributions by party."""
        election_cycle = request.query_params.get('election_cycle')
        
        queryset = self.get_queryset()
        if election_cycle:
            queryset = queryset.filter(election_cycle=election_cycle)
        
        breakdown = queryset.values('recipient_party').annotate(
            total_amount=Sum('amount'),
            contribution_count=Count('id')
        ).order_by('-total_amount')
        
        return Response(list(breakdown))


class CharitableGrantViewSet(viewsets.ModelViewSet):
    """API endpoint for charitable grants."""
    queryset = CharitableGrant.objects.all()
    serializer_class = CharitableGrantSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['company', 'fiscal_year', 'recipient_category']
    search_fields = ['company__name', 'recipient_name', 'grant_description']
    ordering_fields = ['fiscal_year', 'amount', 'created_at']
    ordering = ['-fiscal_year']

    @action(detail=False, methods=['get'])
    def category_breakdown(self, request):
        """Get charitable grants by category."""
        company_id = request.query_params.get('company')
        fiscal_year = request.query_params.get('fiscal_year')
        
        queryset = self.get_queryset()
        
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        if fiscal_year:
            queryset = queryset.filter(fiscal_year=fiscal_year)
        
        breakdown = queryset.values('recipient_category').annotate(
            total_amount=Sum('amount'),
            grant_count=Count('id')
        ).order_by('-total_amount')
        
        return Response(list(breakdown))

    @action(detail=False, methods=['get'])
    def grant_trends(self, request):
        """Get charitable grant trends over time."""
        company_id = request.query_params.get('company')
        start_year = request.query_params.get('start_year', 2020)
        end_year = request.query_params.get('end_year', timezone.now().year)
        
        queryset = self.get_queryset().filter(
            fiscal_year__gte=start_year,
            fiscal_year__lte=end_year
        )
        
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        trends = queryset.values('fiscal_year').annotate(
            total_amount=Sum('amount'),
            grant_count=Count('id')
        ).order_by('fiscal_year')
        
        return Response(list(trends))
