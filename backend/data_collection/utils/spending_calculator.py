"""
Utility functions for calculating company spending across different categories.
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, Optional, Tuple, List
from django.db.models import Sum, Q
from django.db.models.query import QuerySet

from ..models import Company, LobbyingReport, PoliticalContribution, CharitableGrant


class SpendingCalculator:
    """
    Centralized class for calculating company spending across different categories.
    Handles the complexity of aggregating data from multiple sources.
    """
    
    @staticmethod
    def calculate_company_spending(
        company: Company,
        category: str = 'all',
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Decimal]:
        """
        Calculate spending for a company across specified categories and date range.
        
        Args:
            company: The company to calculate spending for
            category: Category to calculate ('all', 'lobbying', 'charitable', 'political')
            start_date: Start date for filtering (optional)
            end_date: End date for filtering (optional)
            
        Returns:
            Dictionary with spending amounts by category
        """
        result = {
            'lobbying': Decimal('0'),
            'charitable': Decimal('0'), 
            'political': Decimal('0'),
            'total': Decimal('0')
        }
        
        # Calculate lobbying spending
        if category in ['all', 'lobbying']:
            result['lobbying'] = SpendingCalculator._calculate_lobbying_spending(
                company, start_date, end_date
            )
        
        # Calculate charitable spending
        if category in ['all', 'charitable']:
            result['charitable'] = SpendingCalculator._calculate_charitable_spending(
                company, start_date, end_date
            )
        
        # Calculate political spending
        if category in ['all', 'political']:
            result['political'] = SpendingCalculator._calculate_political_spending(
                company, start_date, end_date
            )
        
        # Calculate total
        result['total'] = result['lobbying'] + result['charitable'] + result['political']
        
        return result
    
    @staticmethod
    def _calculate_lobbying_spending(
        company: Company,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Decimal:
        """Calculate lobbying spending for a company."""
        queryset = company.lobbying_reports.all()
        
        # Apply date filters
        if start_date:
            # Convert date to year for lobbying reports
            start_year = start_date.year
            queryset = queryset.filter(year__gte=start_year)
        
        if end_date:
            end_year = end_date.year
            queryset = queryset.filter(year__lte=end_year)
        
        total = queryset.aggregate(total=Sum('amount_spent'))['total']
        return total or Decimal('0')
    
    @staticmethod
    def _calculate_charitable_spending(
        company: Company,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Decimal:
        """Calculate charitable spending for a company."""
        queryset = company.charitable_grants.all()
        
        # Apply date filters
        if start_date:
            start_year = start_date.year
            queryset = queryset.filter(fiscal_year__gte=start_year)
        
        if end_date:
            end_year = end_date.year
            queryset = queryset.filter(fiscal_year__lte=end_year)
        
        total = queryset.aggregate(total=Sum('amount'))['total']
        return total or Decimal('0')
    
    @staticmethod
    def _calculate_political_spending(
        company: Company,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Decimal:
        """Calculate political spending for a company."""
        # Note: This is a simplified approach using company name matching
        # In a production system, you'd want a more robust way to link
        # political contributions to companies
        company_name_parts = company.name.split()
        if not company_name_parts:
            return Decimal('0')
        
        # Search for PACs containing the company name
        queryset = PoliticalContribution.objects.filter(
            company_pac_id__icontains=company_name_parts[0]
        )
        
        # Apply date filters
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        total = queryset.aggregate(total=Sum('amount'))['total']
        return total or Decimal('0')
    
    @staticmethod
    def calculate_spending_breakdown(
        company: Company,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, any]:
        """
        Calculate detailed spending breakdown including category details.
        
        Returns:
            Dictionary with detailed breakdown including charitable categories
        """
        spending = SpendingCalculator.calculate_company_spending(
            company, 'all', start_date, end_date
        )
        
        # Get charitable breakdown by category
        charitable_queryset = company.charitable_grants.all()
        if start_date:
            charitable_queryset = charitable_queryset.filter(fiscal_year__gte=start_date.year)
        if end_date:
            charitable_queryset = charitable_queryset.filter(fiscal_year__lte=end_date.year)
        
        charitable_by_category = charitable_queryset.values('recipient_category').annotate(
            total=Sum('amount'),
            count=Sum('id')  # Count of grants
        ).order_by('-total')
        
        return {
            'spending_totals': {
                'lobbying': float(spending['lobbying']),
                'charitable': float(spending['charitable']),
                'political': float(spending['political']),
                'total': float(spending['total'])
            },
            'charitable_breakdown': list(charitable_by_category)
        }
    
    @staticmethod
    def get_top_spenders(
        limit: int = 10,
        category: str = 'all',
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, any]]:
        """
        Get top spending companies across all categories.
        
        Args:
            limit: Number of companies to return
            category: Category to rank by ('all', 'lobbying', 'charitable', 'political')
            start_date: Start date for filtering
            end_date: End date for filtering
            
        Returns:
            List of companies with their spending data, sorted by total spending
        """
        companies = Company.objects.all()
        results = []
        
        for company in companies:
            spending = SpendingCalculator.calculate_company_spending(
                company, category, start_date, end_date
            )
            
            # Only include companies with spending > 0
            if spending['total'] > 0:
                results.append({
                    'company': {
                        'id': company.id,
                        'name': company.name,
                        'ticker': company.ticker,
                    },
                    'spending': {
                        'lobbying': float(spending['lobbying']),
                        'charitable': float(spending['charitable']),
                        'political': float(spending['political']),
                        'total': float(spending['total']),
                    }
                })
        
        # Sort by total spending and return top N
        results.sort(key=lambda x: x['spending']['total'], reverse=True)
        return results[:limit]
    
    @staticmethod
    def filter_companies_by_spending(
        queryset: QuerySet,
        min_spending: Optional[Decimal] = None,
        max_spending: Optional[Decimal] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[int]:
        """
        Filter companies by spending criteria and return list of company IDs.
        
        Args:
            queryset: Initial queryset of companies
            min_spending: Minimum total spending threshold
            max_spending: Maximum total spending threshold
            start_date: Start date for spending calculation
            end_date: End date for spending calculation
            
        Returns:
            List of company IDs that meet spending criteria
        """
        if not min_spending and not max_spending:
            return list(queryset.values_list('id', flat=True))
        
        matching_company_ids = []
        
        for company in queryset:
            spending = SpendingCalculator.calculate_company_spending(
                company, 'all', start_date, end_date
            )
            
            total_spending = spending['total']
            
            # Check spending criteria
            if min_spending and total_spending < min_spending:
                continue
            if max_spending and total_spending > max_spending:
                continue
            
            matching_company_ids.append(company.id)
        
        return matching_company_ids
    
    @staticmethod
    def get_spending_statistics() -> Dict[str, any]:
        """
        Get overall spending statistics across the platform.
        
        Returns:
            Dictionary with aggregate spending statistics
        """
        # Calculate totals across all companies
        total_lobbying = LobbyingReport.objects.aggregate(
            total=Sum('amount_spent')
        )['total'] or Decimal('0')
        
        total_charitable = CharitableGrant.objects.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        
        total_political = PoliticalContribution.objects.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        
        total_spending = total_lobbying + total_charitable + total_political
        
        # Get counts
        total_companies = Company.objects.count()
        companies_with_lobbying = Company.objects.filter(
            lobbying_reports__isnull=False
        ).distinct().count()
        companies_with_charitable = Company.objects.filter(
            charitable_grants__isnull=False
        ).distinct().count()
        companies_with_political = PoliticalContribution.objects.values(
            'company_pac_id'
        ).distinct().count()
        
        return {
            'total_spending': float(total_spending),
            'spending_breakdown': {
                'lobbying': float(total_lobbying),
                'charitable': float(total_charitable),
                'political': float(total_political)
            },
            'total_companies': total_companies,
            'companies_by_category': {
                'lobbying': companies_with_lobbying,
                'charitable': companies_with_charitable,
                'political': companies_with_political
            },
            'average_spending_per_company': (
                float(total_spending / total_companies) if total_companies > 0 else 0
            )
        }
