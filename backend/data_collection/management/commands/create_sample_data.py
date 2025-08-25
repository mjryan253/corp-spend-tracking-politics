from django.core.management.base import BaseCommand
from django.utils import timezone
from data_collection.models import Company, FinancialSummary, LobbyingReport, PoliticalContribution, CharitableGrant
from decimal import Decimal
from datetime import date


class Command(BaseCommand):
    help = 'Create sample data for testing the corporate spending tracker'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create sample companies
        apple = Company.objects.create(
            name='Apple Inc.',
            ticker='AAPL',
            cik='0000320193',
            headquarters_location='Cupertino, CA'
        )

        microsoft = Company.objects.create(
            name='Microsoft Corporation',
            ticker='MSFT',
            cik='0000789019',
            headquarters_location='Redmond, WA'
        )

        google = Company.objects.create(
            name='Alphabet Inc.',
            ticker='GOOGL',
            cik='0001652044',
            headquarters_location='Mountain View, CA'
        )

        # Create financial summaries
        FinancialSummary.objects.create(
            company=apple,
            fiscal_year=2023,
            total_revenue=Decimal('383285000000'),
            net_income=Decimal('96995000000')
        )

        FinancialSummary.objects.create(
            company=microsoft,
            fiscal_year=2023,
            total_revenue=Decimal('211915000000'),
            net_income=Decimal('72361000000')
        )

        FinancialSummary.objects.create(
            company=google,
            fiscal_year=2023,
            total_revenue=Decimal('307394000000'),
            net_income=Decimal('73737000000')
        )

        # Create lobbying reports
        LobbyingReport.objects.create(
            company=apple,
            year=2024,
            quarter=1,
            amount_spent=Decimal('2500000'),
            specific_issues='Privacy legislation, antitrust reform, trade policy',
            report_url='https://example.com/apple-lobbying-2024-q1'
        )

        LobbyingReport.objects.create(
            company=microsoft,
            year=2024,
            quarter=1,
            amount_spent=Decimal('3200000'),
            specific_issues='Cybersecurity, cloud computing regulations, AI policy',
            report_url='https://example.com/microsoft-lobbying-2024-q1'
        )

        LobbyingReport.objects.create(
            company=google,
            year=2024,
            quarter=1,
            amount_spent=Decimal('2800000'),
            specific_issues='Digital advertising, content moderation, AI ethics',
            report_url='https://example.com/google-lobbying-2024-q1'
        )

        # Create political contributions
        PoliticalContribution.objects.create(
            company_pac_id='Apple Inc. PAC',
            recipient_name='Sen. John Smith',
            recipient_party='Democratic',
            amount=Decimal('5000'),
            date=date(2024, 1, 15),
            election_cycle='2024'
        )

        PoliticalContribution.objects.create(
            company_pac_id='Microsoft PAC',
            recipient_name='Rep. Jane Doe',
            recipient_party='Republican',
            amount=Decimal('3500'),
            date=date(2024, 2, 20),
            election_cycle='2024'
        )

        PoliticalContribution.objects.create(
            company_pac_id='Alphabet Inc. PAC',
            recipient_name='Sen. Bob Johnson',
            recipient_party='Democratic',
            amount=Decimal('4500'),
            date=date(2024, 3, 10),
            election_cycle='2024'
        )

        # Create charitable grants
        CharitableGrant.objects.create(
            company=apple,
            recipient_name='American Red Cross',
            recipient_ein='53-0196605',
            amount=Decimal('1000000'),
            fiscal_year=2023,
            grant_description='Disaster relief and emergency response',
            recipient_category='Humanitarian'
        )

        CharitableGrant.objects.create(
            company=microsoft,
            recipient_name='University of Washington Foundation',
            recipient_ein='91-1077680',
            amount=Decimal('500000'),
            fiscal_year=2023,
            grant_description='Computer science education and research',
            recipient_category='Education'
        )

        CharitableGrant.objects.create(
            company=google,
            recipient_name='St. Mary\'s Catholic Church',
            recipient_ein='94-3068481',
            amount=Decimal('250000'),
            fiscal_year=2023,
            grant_description='Community outreach and youth programs',
            recipient_category='Religious'
        )

        CharitableGrant.objects.create(
            company=apple,
            recipient_name='Stanford University',
            recipient_ein='94-1156365',
            amount=Decimal('750000'),
            fiscal_year=2023,
            grant_description='Technology innovation and research',
            recipient_category='Education'
        )

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )
        self.stdout.write(f'Created {Company.objects.count()} companies')
        self.stdout.write(f'Created {FinancialSummary.objects.count()} financial summaries')
        self.stdout.write(f'Created {LobbyingReport.objects.count()} lobbying reports')
        self.stdout.write(f'Created {PoliticalContribution.objects.count()} political contributions')
        self.stdout.write(f'Created {CharitableGrant.objects.count()} charitable grants')
