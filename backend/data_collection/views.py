
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json
import os
from django.conf import settings
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Company, FinancialSummary, LobbyingReport, PoliticalContribution, CharitableGrant
from .serializers import (
    CompanySerializer, CompanyDetailSerializer, FinancialSummarySerializer,
    LobbyingReportSerializer, PoliticalContributionSerializer, CharitableGrantSerializer
)
from .utils.spending_calculator import SpendingCalculator

# Simple logging function
@extend_schema(
    tags=['system'],
    summary="Log frontend events",
    description="Receive and store frontend logging events for debugging purposes",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'timestamp': {'type': 'string', 'format': 'date-time'},
                'level': {'type': 'string', 'enum': ['INFO', 'WARNING', 'ERROR', 'DEBUG']},
                'message': {'type': 'string'},
                'data': {'type': 'object'},
                'userAgent': {'type': 'string'},
                'url': {'type': 'string'},
            }
        }
    },
    responses={
        200: {
            'type': 'object',
            'properties': {
                'status': {'type': 'string', 'example': 'success'}
            }
        }
    }
)
@api_view(['POST'])
def log_frontend(request):
    """Simple endpoint to receive frontend logs"""
    try:
        log_data = request.data
        timestamp = log_data.get('timestamp', datetime.now().isoformat())
        level = log_data.get('level', 'INFO')
        message = log_data.get('message', '')
        data = log_data.get('data')
        user_agent = log_data.get('userAgent', '')
        url = log_data.get('url', '')
        
        # Create log entry
        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'message': message,
            'data': data,
            'user_agent': user_agent,
            'url': url
        }
        
        # Write to log file
        log_file_path = os.path.join(settings.BASE_DIR, 'frontend_debug.log')
        
        with open(log_file_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        
        return Response({'status': 'success'}, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@extend_schema(
    tags=['system'],
    summary="Get frontend logs",
    description="Retrieve the last 50 frontend log entries for debugging",
    responses={
        200: {
            'type': 'object',
            'properties': {
                'logs': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'timestamp': {'type': 'string'},
                            'level': {'type': 'string'},
                            'message': {'type': 'string'},
                            'data': {'type': 'object'},
                            'user_agent': {'type': 'string'},
                            'url': {'type': 'string'},
                        }
                    }
                }
            }
        }
    }
)
@api_view(['GET'])
def get_logs(request):
    """Simple endpoint to retrieve logs"""
    try:
        log_file_path = os.path.join(settings.BASE_DIR, 'frontend_debug.log')
        
        if not os.path.exists(log_file_path):
            return Response({'logs': []}, status=status.HTTP_200_OK)
        
        logs = []
        with open(log_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    log_entry = json.loads(line.strip())
                    logs.append(log_entry)
                except json.JSONDecodeError:
                    continue
        
        # Return last 50 logs
        logs = logs[-50:]
        
        return Response({'logs': logs}, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@extend_schema(
    tags=['analytics'],
    summary="Get dashboard summary",
    description="Retrieve comprehensive dashboard statistics including total companies, spending breakdown, and recent activity",
    responses={
        200: {
            'type': 'object',
            'properties': {
                'total_companies': {'type': 'integer', 'example': 150},
                'total_spending': {'type': 'number', 'example': 500000000},
                'spending_breakdown': {
                    'type': 'object',
                    'properties': {
                        'lobbying': {'type': 'number', 'example': 200000000},
                        'political': {'type': 'number', 'example': 150000000},
                        'charitable': {'type': 'number', 'example': 150000000}
                    }
                },
                'recent_activity': {
                    'type': 'object',
                    'properties': {
                        'new_companies': {'type': 'integer', 'example': 5},
                        'new_reports': {'type': 'integer', 'example': 25},
                        'new_contributions': {'type': 'integer', 'example': 100}
                    }
                }
            }
        }
    }
)
@api_view(['GET'])
def dashboard_summary(request):
    """Get dashboard summary statistics"""
    try:
        # Use the spending calculator for consistent statistics
        spending_stats = SpendingCalculator.get_spending_statistics()
        
        # Get recent activity (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        new_companies = Company.objects.filter(
            created_at__gte=thirty_days_ago
        ).count()
        
        new_reports = LobbyingReport.objects.filter(
            created_at__gte=thirty_days_ago
        ).count()
        
        new_contributions = PoliticalContribution.objects.filter(
            created_at__gte=thirty_days_ago
        ).count()
        
        new_grants = CharitableGrant.objects.filter(
            created_at__gte=thirty_days_ago
        ).count()
        
        return Response({
            'total_companies': spending_stats['total_companies'],
            'total_spending': spending_stats['total_spending'],
            'spending_breakdown': spending_stats['spending_breakdown'],
            'companies_by_category': spending_stats['companies_by_category'],
            'average_spending_per_company': spending_stats['average_spending_per_company'],
            'recent_activity': {
                'new_companies': new_companies,
                'new_reports': new_reports,
                'new_contributions': new_contributions,
                'new_grants': new_grants
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@extend_schema(
    tags=['analytics'],
    summary="Get spending comparison data",
    description="Retrieve spending comparison data for all companies, useful for analytics and visualization",
    responses={
        200: {
            'type': 'object',
            'properties': {
                'results': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'company': {
                                'type': 'object',
                                'properties': {
                                    'id': {'type': 'integer'},
                                    'name': {'type': 'string'},
                                    'ticker': {'type': 'string'}
                                }
                            },
                            'spending': {
                                'type': 'object',
                                'properties': {
                                    'lobbying': {'type': 'number'},
                                    'charitable': {'type': 'number'},
                                    'political': {'type': 'number'},
                                    'total': {'type': 'number'}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
)
@api_view(['GET'])
def spending_comparison(request):
    """Get spending comparison data for analytics"""
    try:
        # Parse optional parameters
        limit = int(request.GET.get('limit', 100))  # Default to top 100 companies
        category = request.GET.get('category', 'all')
        
        # Use the spending calculator for consistent data
        results = SpendingCalculator.get_top_spenders(
            limit=limit,
            category=category
        )
        
        return Response({
            'results': results,
            'metadata': {
                'total_results': len(results),
                'category_filter': category,
                'limit': limit
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema_view(
    list=extend_schema(
        tags=['companies'],
        summary="List companies",
        description="Retrieve a paginated list of all companies with optional filtering and search",
        parameters=[
            OpenApiParameter(name='search', type=OpenApiTypes.STR, description='Search in name, ticker, or CIK'),
            OpenApiParameter(name='ticker', type=OpenApiTypes.STR, description='Filter by ticker symbol'),
            OpenApiParameter(name='cik', type=OpenApiTypes.STR, description='Filter by SEC CIK'),
            OpenApiParameter(name='page', type=OpenApiTypes.INT, description='Page number for pagination'),
            OpenApiParameter(name='page_size', type=OpenApiTypes.INT, description='Number of items per page (max: 100)'),
        ]
    ),
    retrieve=extend_schema(
        tags=['companies'],
        summary="Get company details",
        description="Get detailed information about a specific company including related data"
    ),
    spending_summary=extend_schema(
        tags=['companies'],
        summary="Get company spending summary",
        description="Get comprehensive spending summary for a company across all categories",
        parameters=[
            OpenApiParameter(name='start_date', type=OpenApiTypes.DATE, description='Filter from date (YYYY-MM-DD)'),
            OpenApiParameter(name='end_date', type=OpenApiTypes.DATE, description='Filter to date (YYYY-MM-DD)'),
        ]
    ),
    top_spenders=extend_schema(
        tags=['companies'],
        summary="Get top spending companies",
        description="Get top spending companies across all categories",
        parameters=[
            OpenApiParameter(name='limit', type=OpenApiTypes.INT, description='Number of companies to return (default: 10)'),
            OpenApiParameter(name='spending_type', type=OpenApiTypes.STR, description='Filter by type (lobbying, political, charitable, all)'),
            OpenApiParameter(name='start_date', type=OpenApiTypes.DATE, description='Filter from date'),
            OpenApiParameter(name='end_date', type=OpenApiTypes.DATE, description='Filter to date'),
        ]
    ),
    search=extend_schema(
        tags=['companies'],
        summary="Advanced company search",
        description="Advanced search with multiple criteria and filters",
        parameters=[
            OpenApiParameter(name='q', type=OpenApiTypes.STR, description='Search query (name, ticker, CIK)'),
            OpenApiParameter(name='min_spending', type=OpenApiTypes.DECIMAL, description='Minimum total spending'),
            OpenApiParameter(name='max_spending', type=OpenApiTypes.DECIMAL, description='Maximum total spending'),
            OpenApiParameter(name='has_lobbying', type=OpenApiTypes.BOOL, description='Filter companies with lobbying data'),
            OpenApiParameter(name='has_charitable', type=OpenApiTypes.BOOL, description='Filter companies with charitable data'),
            OpenApiParameter(name='has_political', type=OpenApiTypes.BOOL, description='Filter companies with political data'),
        ]
    )
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
        
        # Parse date range from query params
        start_date = None
        end_date = None
        
        if request.query_params.get('start_date'):
            try:
                start_date = datetime.strptime(
                    request.query_params.get('start_date'), '%Y-%m-%d'
                ).date()
            except ValueError:
                pass
        
        if request.query_params.get('end_date'):
            try:
                end_date = datetime.strptime(
                    request.query_params.get('end_date'), '%Y-%m-%d'
                ).date()
            except ValueError:
                pass
        
        # Use the spending calculator for consistent logic
        spending_data = SpendingCalculator.calculate_spending_breakdown(
            company, start_date, end_date
        )
        
        # Get recent financial data
        latest_financial = company.financial_summaries.order_by('-fiscal_year').first()
        
        # Count records within date range
        lobbying_qs = company.lobbying_reports.all()
        charitable_qs = company.charitable_grants.all()
        political_qs = PoliticalContribution.objects.filter(
            company_pac_id__icontains=company.name.split()[0]
        )
        
        if start_date:
            lobbying_qs = lobbying_qs.filter(year__gte=start_date.year)
            charitable_qs = charitable_qs.filter(fiscal_year__gte=start_date.year)
            political_qs = political_qs.filter(date__gte=start_date)
        
        if end_date:
            lobbying_qs = lobbying_qs.filter(year__lte=end_date.year)
            charitable_qs = charitable_qs.filter(fiscal_year__lte=end_date.year)
            political_qs = political_qs.filter(date__lte=end_date)
        
        return Response({
            'company': {
                'id': company.id,
                'name': company.name,
                'ticker': company.ticker,
                'cik': company.cik,
            },
            **spending_data,
            'financial_context': {
                'latest_revenue': float(latest_financial.total_revenue) if latest_financial and latest_financial.total_revenue else None,
                'latest_net_income': float(latest_financial.net_income) if latest_financial and latest_financial.net_income else None,
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
        
        # Parse optional date filters
        start_date = None
        end_date = None
        
        if request.query_params.get('start_date'):
            try:
                start_date = datetime.strptime(
                    request.query_params.get('start_date'), '%Y-%m-%d'
                ).date()
            except ValueError:
                pass
        
        if request.query_params.get('end_date'):
            try:
                end_date = datetime.strptime(
                    request.query_params.get('end_date'), '%Y-%m-%d'
                ).date()
            except ValueError:
                pass
        
        # Use the centralized spending calculator
        results = SpendingCalculator.get_top_spenders(
            limit=limit,
            category=category,
            start_date=start_date,
            end_date=end_date
        )
        
        return Response(results)

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
            min_decimal = Decimal(min_spending) if min_spending else None
            max_decimal = Decimal(max_spending) if max_spending else None
            
            companies_with_spending = SpendingCalculator.filter_companies_by_spending(
                queryset=queryset,
                min_spending=min_decimal,
                max_spending=max_decimal
            )
            
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


@extend_schema_view(
    list=extend_schema(tags=['financial']),
    retrieve=extend_schema(tags=['financial']),
    financial_ratios=extend_schema(
        tags=['financial'],
        summary="Get financial ratios",
        description="Calculate financial ratios for companies including profit margins"
    )
)
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


@extend_schema_view(
    list=extend_schema(tags=['lobbying']),
    retrieve=extend_schema(tags=['lobbying']),
    spending_trends=extend_schema(
        tags=['lobbying'],
        summary="Get lobbying spending trends",
        description="Get lobbying spending trends over time by year and quarter"
    ),
    top_issues=extend_schema(
        tags=['lobbying'],
        summary="Get top lobbied issues",
        description="Get most lobbied issues and top lobbying companies"
    )
)
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


@extend_schema_view(
    list=extend_schema(tags=['political']),
    retrieve=extend_schema(tags=['political']),
    contribution_trends=extend_schema(
        tags=['political'],
        summary="Get contribution trends",
        description="Get political contribution trends over time"
    ),
    party_breakdown=extend_schema(
        tags=['political'],
        summary="Get party breakdown",
        description="Get political contributions broken down by party"
    )
)
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


@extend_schema_view(
    list=extend_schema(tags=['charitable']),
    retrieve=extend_schema(tags=['charitable']),
    category_breakdown=extend_schema(
        tags=['charitable'],
        summary="Get category breakdown",
        description="Get charitable grants broken down by recipient category"
    ),
    grant_trends=extend_schema(
        tags=['charitable'],
        summary="Get grant trends",
        description="Get charitable grant trends over time"
    )
)
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
