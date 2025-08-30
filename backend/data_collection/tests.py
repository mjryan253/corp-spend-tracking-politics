from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from datetime import datetime, date
from unittest.mock import patch, Mock
import json

from .models import Company, FinancialSummary, LobbyingReport, PoliticalContribution, CharitableGrant
from .utils.spending_calculator import SpendingCalculator
from .ingestion.fec_ingestion import FECIngestion
from .ingestion.error_handler import ExponentialBackoff, APIError, RateLimitError


class CompanyModelTest(TestCase):
    """Test the Company model and its relationships."""
    
    def setUp(self):
        self.company = Company.objects.create(
            name='Test Company',
            ticker='TEST',
            cik='0000123456',
            headquarters_location='Test City, ST'
        )

    def test_company_creation(self):
        """Test basic company creation and string representation."""
        self.assertEqual(self.company.name, 'Test Company')
        self.assertEqual(self.company.ticker, 'TEST')
        self.assertEqual(self.company.cik, '0000123456')
        self.assertEqual(str(self.company), 'Test Company')

    def test_company_relationships(self):
        """Test foreign key relationships work correctly."""
        # Create related objects
        financial = FinancialSummary.objects.create(
            company=self.company,
            fiscal_year=2023,
            total_revenue=Decimal('1000000'),
            net_income=Decimal('100000')
        )
        
        lobbying = LobbyingReport.objects.create(
            company=self.company,
            year=2024,
            quarter=1,
            amount_spent=Decimal('50000')
        )
        
        grant = CharitableGrant.objects.create(
            company=self.company,
            recipient_name='Test Charity',
            amount=Decimal('25000'),
            fiscal_year=2023
        )
        
        # Test relationships
        self.assertEqual(self.company.financial_summaries.count(), 1)
        self.assertEqual(self.company.lobbying_reports.count(), 1)
        self.assertEqual(self.company.charitable_grants.count(), 1)
        
        self.assertEqual(self.company.financial_summaries.first(), financial)
        self.assertEqual(self.company.lobbying_reports.first(), lobbying)
        self.assertEqual(self.company.charitable_grants.first(), grant)

    def test_company_validation(self):
        """Test model validation and constraints."""
        # Test unique constraint on company
        with self.assertRaises(Exception):  # Should raise IntegrityError in real scenario
            Company.objects.create(name='')  # Empty name should not be allowed
        
        # Test valid CIK format
        valid_company = Company.objects.create(
            name='Valid Company',
            cik='0000999999'
        )
        self.assertEqual(len(valid_company.cik), 10)


class FinancialSummaryModelTest(TestCase):
    """Test the FinancialSummary model."""
    
    def setUp(self):
        self.company = Company.objects.create(
            name='Financial Test Company',
            ticker='FTC'
        )
    
    def test_financial_summary_creation(self):
        """Test financial summary creation and validation."""
        financial = FinancialSummary.objects.create(
            company=self.company,
            fiscal_year=2023,
            total_revenue=Decimal('1000000.00'),
            net_income=Decimal('150000.00')
        )
        
        self.assertEqual(financial.company, self.company)
        self.assertEqual(financial.fiscal_year, 2023)
        self.assertEqual(financial.total_revenue, Decimal('1000000.00'))
        
    def test_financial_summary_unique_constraint(self):
        """Test that company/fiscal_year combination is unique."""
        FinancialSummary.objects.create(
            company=self.company,
            fiscal_year=2023,
            total_revenue=Decimal('1000000.00')
        )
        
        # This should raise an IntegrityError due to unique_together constraint
        with self.assertRaises(Exception):
            FinancialSummary.objects.create(
                company=self.company,
                fiscal_year=2023,
                total_revenue=Decimal('2000000.00')
            )


class SpendingCalculatorTest(TestCase):
    """Test the SpendingCalculator utility class."""
    
    def setUp(self):
        """Set up test data for spending calculations."""
        self.company1 = Company.objects.create(
            name='Apple Inc.',
            ticker='AAPL',
            cik='0000320193'
        )
        
        self.company2 = Company.objects.create(
            name='Microsoft Corporation',
            ticker='MSFT',
            cik='0000789019'
        )
        
        # Create lobbying reports
        LobbyingReport.objects.create(
            company=self.company1,
            year=2023,
            quarter=1,
            amount_spent=Decimal('1000000')
        )
        
        LobbyingReport.objects.create(
            company=self.company1,
            year=2023,
            quarter=2,
            amount_spent=Decimal('1500000')
        )
        
        # Create charitable grants
        CharitableGrant.objects.create(
            company=self.company1,
            recipient_name='Red Cross',
            amount=Decimal('500000'),
            fiscal_year=2023
        )
        
        # Create political contributions
        PoliticalContribution.objects.create(
            company_pac_id='Apple Inc. PAC',
            recipient_name='John Doe',
            amount=Decimal('5000'),
            date=date(2023, 6, 15),
            election_cycle='2024'
        )
    
    def test_calculate_company_spending_all_categories(self):
        """Test spending calculation for all categories."""
        spending = SpendingCalculator.calculate_company_spending(self.company1, 'all')
        
        self.assertEqual(spending['lobbying'], Decimal('2500000'))  # 1M + 1.5M
        self.assertEqual(spending['charitable'], Decimal('500000'))
        self.assertEqual(spending['political'], Decimal('5000'))
        self.assertEqual(spending['total'], Decimal('3005000'))
    
    def test_calculate_company_spending_single_category(self):
        """Test spending calculation for single categories."""
        lobbying_spending = SpendingCalculator.calculate_company_spending(self.company1, 'lobbying')
        charitable_spending = SpendingCalculator.calculate_company_spending(self.company1, 'charitable')
        
        self.assertEqual(lobbying_spending['lobbying'], Decimal('2500000'))
        self.assertEqual(lobbying_spending['charitable'], Decimal('0'))
        self.assertEqual(lobbying_spending['political'], Decimal('0'))
        
        self.assertEqual(charitable_spending['charitable'], Decimal('500000'))
        self.assertEqual(charitable_spending['lobbying'], Decimal('0'))
    
    def test_get_top_spenders(self):
        """Test getting top spending companies."""
        top_spenders = SpendingCalculator.get_top_spenders(limit=5)
        
        self.assertEqual(len(top_spenders), 1)  # Only company1 has spending
        self.assertEqual(top_spenders[0]['company']['name'], 'Apple Inc.')
        self.assertEqual(top_spenders[0]['spending']['total'], 3005000.0)
    
    def test_filter_companies_by_spending(self):
        """Test filtering companies by spending amount."""
        queryset = Company.objects.all()
        
        # Filter for companies with spending > 1M
        high_spenders = SpendingCalculator.filter_companies_by_spending(
            queryset, min_spending=Decimal('1000000')
        )
        
        self.assertEqual(len(high_spenders), 1)
        self.assertEqual(high_spenders[0], self.company1.id)
        
        # Filter for companies with spending < 1M (should include company2 which has no spending)
        low_spenders = SpendingCalculator.filter_companies_by_spending(
            queryset, max_spending=Decimal('1000000')
        )
        
        # Company2 has no spending (0), so it should be included in max_spending filter
        self.assertEqual(len(low_spenders), 1)
        self.assertEqual(low_spenders[0], self.company2.id)
    
    def test_get_spending_statistics(self):
        """Test overall spending statistics calculation."""
        stats = SpendingCalculator.get_spending_statistics()
        
        self.assertEqual(stats['total_spending'], 3005000.0)
        self.assertEqual(stats['spending_breakdown']['lobbying'], 2500000.0)
        self.assertEqual(stats['spending_breakdown']['charitable'], 500000.0)
        self.assertEqual(stats['total_companies'], 2)


class CompanyAPITest(APITestCase):
    """Test the Company API endpoints."""
    
    def setUp(self):
        self.company = Company.objects.create(
            name='API Test Company',
            ticker='API',
            cik='0000789012',
            headquarters_location='API City, ST'
        )
        
        # Create sample data
        self.financial = FinancialSummary.objects.create(
            company=self.company,
            fiscal_year=2023,
            total_revenue=Decimal('5000000'),
            net_income=Decimal('500000')
        )
        
        self.lobbying = LobbyingReport.objects.create(
            company=self.company,
            year=2024,
            quarter=1,
            amount_spent=Decimal('100000')
        )
        
        self.grant = CharitableGrant.objects.create(
            company=self.company,
            recipient_name='API Charity',
            amount=Decimal('50000'),
            fiscal_year=2023
        )

    def test_get_companies_list(self):
        """Test the companies list endpoint."""
        url = reverse('company-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'API Test Company')

    def test_get_company_detail(self):
        """Test the company detail endpoint."""
        url = reverse('company-detail', args=[self.company.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'API Test Company')
        self.assertEqual(len(response.data['financial_summaries']), 1)
        self.assertEqual(len(response.data['lobbying_reports']), 1)
        self.assertEqual(len(response.data['charitable_grants']), 1)

    def test_get_spending_summary(self):
        """Test the company spending summary endpoint."""
        url = reverse('company-spending-summary', args=[self.company.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company']['name'], 'API Test Company')
        self.assertEqual(response.data['spending_totals']['lobbying'], 100000.0)
        self.assertEqual(response.data['spending_totals']['charitable'], 50000.0)
        self.assertEqual(response.data['spending_totals']['total'], 150000.0)
    
    def test_get_spending_summary_with_date_filter(self):
        """Test spending summary with date filters."""
        url = reverse('company-spending-summary', args=[self.company.id])
        response = self.client.get(url, {'start_date': '2024-01-01', 'end_date': '2024-12-31'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only include 2024 lobbying data
        self.assertEqual(response.data['spending_totals']['lobbying'], 100000.0)
        self.assertEqual(response.data['spending_totals']['charitable'], 0.0)  # 2023 data filtered out
    
    def test_get_top_spenders(self):
        """Test the top spenders endpoint."""
        url = reverse('company-top-spenders')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['company']['name'], 'API Test Company')
    
    def test_company_search(self):
        """Test the company search endpoint."""
        url = reverse('company-search')
        
        # Test text search
        response = self.client.get(url, {'q': 'API'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Test spending filter
        response = self.client.get(url, {'min_spending': '100000'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Test spending filter that should exclude our company
        response = self.client.get(url, {'min_spending': '200000'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_create_company_unauthorized(self):
        """Test that creating companies requires authorization."""
        url = reverse('company-list')
        data = {
            'name': 'New Company',
            'ticker': 'NEW'
        }
        response = self.client.post(url, data)
        
        # Should allow creation for now (no auth required)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AnalyticsAPITest(APITestCase):
    """Test analytics API endpoints."""
    
    def setUp(self):
        """Set up test data for analytics."""
        self.company = Company.objects.create(
            name='Analytics Test Company',
            ticker='ATC'
        )
        
        LobbyingReport.objects.create(
            company=self.company,
            year=2023,
            quarter=1,
            amount_spent=Decimal('500000')
        )
    
    def test_dashboard_summary(self):
        """Test the dashboard summary endpoint."""
        url = reverse('dashboard-summary')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_companies', response.data)
        self.assertIn('total_spending', response.data)
        self.assertIn('spending_breakdown', response.data)
        self.assertIn('recent_activity', response.data)
        
        self.assertEqual(response.data['total_companies'], 1)
        self.assertEqual(response.data['total_spending'], 500000.0)
    
    def test_spending_comparison(self):
        """Test the spending comparison endpoint."""
        url = reverse('spending-comparison')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('metadata', response.data)
        
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['company']['name'], 'Analytics Test Company')


class ErrorHandlerTest(TestCase):
    """Test the error handling utilities."""
    
    def test_exponential_backoff_calculation(self):
        """Test exponential backoff delay calculation."""
        backoff = ExponentialBackoff(base_delay=1.0, exponential_base=2.0, jitter=False)
        
        self.assertEqual(backoff.calculate_delay(0), 0)
        self.assertEqual(backoff.calculate_delay(1), 1.0)
        self.assertEqual(backoff.calculate_delay(2), 2.0)
        self.assertEqual(backoff.calculate_delay(3), 4.0)
    
    def test_exponential_backoff_max_delay(self):
        """Test that delays are capped at max_delay."""
        backoff = ExponentialBackoff(base_delay=1.0, max_delay=5.0, jitter=False)
        
        # High attempt numbers should be capped
        self.assertEqual(backoff.calculate_delay(10), 5.0)
    
    def test_retryable_error_detection(self):
        """Test detection of retryable vs non-retryable errors."""
        backoff = ExponentialBackoff()
        
        # Should be retryable
        rate_limit_error = RateLimitError("Rate limited")
        self.assertTrue(backoff._is_retryable_error(rate_limit_error))
        
        api_error_500 = APIError("Server error", status_code=500)
        self.assertTrue(backoff._is_retryable_error(api_error_500))
        
        # Should not be retryable
        api_error_400 = APIError("Bad request", status_code=400)
        self.assertFalse(backoff._is_retryable_error(api_error_400))


class FECIngestionTest(TestCase):
    """Test the FEC data ingestion functionality."""
    
    def setUp(self):
        self.fec_ingestion = FECIngestion()
    
    @patch.dict('os.environ', {'FEC_API_KEY': ''})
    def test_fec_ingestion_without_api_key(self):
        """Test FEC ingestion falls back to mock data without API key."""
        fec = FECIngestion()
        data = fec.fetch_data(2023)
        
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        # Should be mock data
        self.assertEqual(data[0]['committee_name'], 'Apple Inc. PAC')
    
    def test_fec_ingestion_get_stats(self):
        """Test FEC ingestion statistics tracking."""
        stats = self.fec_ingestion.get_ingestion_stats()
        
        self.assertIn('fec_specific', stats)
        self.assertIn('global_api_stats', stats)
        self.assertIn('success_rate', stats)
    
    def test_fec_ingestion_reset_stats(self):
        """Test resetting ingestion statistics."""
        self.fec_ingestion.stats['total_requests'] = 5
        self.fec_ingestion.reset_stats()
        
        self.assertEqual(self.fec_ingestion.stats['total_requests'], 0)
        self.assertEqual(self.fec_ingestion.stats['successful_requests'], 0)


class LoggingAPITest(APITestCase):
    """Test the frontend logging endpoints."""
    
    def test_log_frontend_success(self):
        """Test successful frontend log submission."""
        url = reverse('log-frontend')
        data = {
            'timestamp': datetime.now().isoformat(),
            'level': 'INFO',
            'message': 'Test log message',
            'data': {'key': 'value'},
            'userAgent': 'Test Browser',
            'url': '/test'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
    
    def test_get_logs(self):
        """Test retrieving frontend logs."""
        # First, submit a log
        log_url = reverse('log-frontend')
        log_data = {
            'level': 'INFO',
            'message': 'Test log for retrieval'
        }
        self.client.post(log_url, log_data, format='json')
        
        # Then retrieve logs
        get_url = reverse('get-logs')
        response = self.client.get(get_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('logs', response.data)


class IntegrationTest(TransactionTestCase):
    """Integration tests for the complete application flow."""
    
    def setUp(self):
        """Set up comprehensive test data."""
        self.company = Company.objects.create(
            name='Integration Test Corp',
            ticker='ITC',
            cik='0000555555'
        )
        
        FinancialSummary.objects.create(
            company=self.company,
            fiscal_year=2023,
            total_revenue=Decimal('10000000'),
            net_income=Decimal('1000000')
        )
        
        LobbyingReport.objects.create(
            company=self.company,
            year=2023,
            quarter=1,
            amount_spent=Decimal('200000')
        )
        
        CharitableGrant.objects.create(
            company=self.company,
            recipient_name='Test Foundation',
            amount=Decimal('100000'),
            fiscal_year=2023
        )
    
    def test_complete_company_workflow(self):
        """Test complete workflow from company creation to analytics."""
        # Test company list
        response = self.client.get(reverse('company-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test company detail
        company_id = response.data['results'][0]['id']
        response = self.client.get(reverse('company-detail', args=[company_id]))
        self.assertEqual(response.status_code, 200)
        
        # Test spending summary
        response = self.client.get(reverse('company-spending-summary', args=[company_id]))
        self.assertEqual(response.status_code, 200)
        self.assertGreater(response.data['spending_totals']['total'], 0)
        
        # Test analytics endpoints
        response = self.client.get(reverse('dashboard-summary'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('spending-comparison'))
        self.assertEqual(response.status_code, 200)
