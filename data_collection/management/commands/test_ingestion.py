from django.core.management.base import BaseCommand
from data_collection.ingestion.fec_ingestion import FECIngestion
from data_collection.ingestion.lobbying_ingestion import LobbyingIngestion
from data_collection.ingestion.irs_ingestion import IRSIngestion
from data_collection.ingestion.sec_ingestion import SECIngestion
from data_collection.ingestion.data_processor import DataProcessor


class Command(BaseCommand):
    help = 'Test the data ingestion pipeline with mock data'

    def handle(self, *args, **options):
        self.stdout.write('Testing data ingestion pipeline...')
        
        # Test FEC ingestion
        self.stdout.write('\n1. Testing FEC Ingestion...')
        fec_ingestion = FECIngestion()
        fec_data = fec_ingestion.fetch_data(year=2024)
        self.stdout.write(f'   FEC: Retrieved {len(fec_data)} records (mock data)')
        
        # Test Lobbying ingestion
        self.stdout.write('\n2. Testing Lobbying Ingestion...')
        lobbying_ingestion = LobbyingIngestion()
        lobbying_data = lobbying_ingestion.fetch_data(year=2024)
        self.stdout.write(f'   Lobbying: Retrieved {len(lobbying_data)} records (mock data)')
        
        # Test IRS ingestion
        self.stdout.write('\n3. Testing IRS Ingestion...')
        irs_ingestion = IRSIngestion()
        irs_data = irs_ingestion.fetch_data(year=2023)
        self.stdout.write(f'   IRS: Retrieved {len(irs_data)} records (mock data)')
        
        # Test SEC ingestion
        self.stdout.write('\n4. Testing SEC Ingestion...')
        sec_ingestion = SECIngestion()
        sec_data = sec_ingestion.fetch_data(year=2023)
        self.stdout.write(f'   SEC: Retrieved {len(sec_data)} records (mock data)')
        
        # Test data processor
        self.stdout.write('\n5. Testing Data Processor...')
        processor = DataProcessor()
        
        # Test company name normalization
        test_names = [
            'Apple Inc.',
            'APPLE CORPORATION',
            'Microsoft Corp',
            'Alphabet Inc.',
        ]
        
        self.stdout.write('   Testing company name normalization:')
        for name in test_names:
            normalized = processor._normalize_company_name(name)
            self.stdout.write(f'     "{name}" -> "{normalized}"')
        
        # Test data quality report
        quality_report = processor.get_data_quality_report()
        self.stdout.write('\n6. Data Quality Report:')
        self.stdout.write(f'   Companies: {quality_report["companies"]["total"]}')
        self.stdout.write(f'   Financial Summaries: {quality_report["financial_summaries"]["total"]}')
        self.stdout.write(f'   Lobbying Reports: {quality_report["lobbying_reports"]["total"]}')
        self.stdout.write(f'   Charitable Grants: {quality_report["charitable_grants"]["total"]}')
        self.stdout.write(f'   Political Contributions: {quality_report["political_contributions"]["total"]}')
        
        # Test company linking
        linking_results = processor.link_companies_across_sources()
        self.stdout.write('\n7. Company Linking Results:')
        self.stdout.write(f'   Total Companies: {linking_results["total_companies"]}')
        self.stdout.write(f'   Linked Companies: {linking_results["linked_companies"]}')
        self.stdout.write(f'   Unlinked Companies: {linking_results["unlinked_companies"]}')
        
        self.stdout.write(
            self.style.SUCCESS('\n✅ Data ingestion pipeline test completed successfully!')
        )
        
        self.stdout.write('\nNote: This test uses mock data. For real data ingestion:')
        self.stdout.write('1. Set up API keys in your .env file')
        self.stdout.write('2. Run: python manage.py ingest_data --dry-run')
        self.stdout.write('3. Run: python manage.py ingest_data')
