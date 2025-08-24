from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from .models import Company, FinancialSummary, LobbyingReport, PoliticalContribution, CharitableGrant


class CompanyModelTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name='Test Company',
            ticker='TEST',
            cik='0000123456',
            headquarters_location='Test City, ST'
        )

    def test_company_creation(self):
        self.assertEqual(self.company.name, 'Test Company')
        self.assertEqual(self.company.ticker, 'TEST')
        self.assertEqual(str(self.company), 'Test Company')

    def test_company_relationships(self):
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


class CompanyAPITest(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name='API Test Company',
            ticker='API',
            cik='0000789012',
            headquarters_location='API City, ST'
        )
        
        # Create sample data
        FinancialSummary.objects.create(
            company=self.company,
            fiscal_year=2023,
            total_revenue=Decimal('5000000'),
            net_income=Decimal('500000')
        )
        
        LobbyingReport.objects.create(
            company=self.company,
            year=2024,
            quarter=1,
            amount_spent=Decimal('100000')
        )
        
        CharitableGrant.objects.create(
            company=self.company,
            recipient_name='API Charity',
            amount=Decimal('50000'),
            fiscal_year=2023
        )

    def test_get_companies_list(self):
        url = reverse('company-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'API Test Company')

    def test_get_company_detail(self):
        url = reverse('company-detail', args=[self.company.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'API Test Company')
        self.assertEqual(len(response.data['financial_summaries']), 1)
        self.assertEqual(len(response.data['lobbying_reports']), 1)
        self.assertEqual(len(response.data['charitable_grants']), 1)

    def test_get_spending_summary(self):
        url = reverse('company-spending-summary', args=[self.company.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company_name'], 'API Test Company')
        self.assertEqual(response.data['total_lobbying'], 100000.0)
        self.assertEqual(response.data['total_charitable'], 50000.0)
        self.assertEqual(response.data['total_spending'], 150000.0)
