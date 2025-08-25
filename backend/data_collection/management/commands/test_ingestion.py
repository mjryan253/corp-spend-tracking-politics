from django.core.management.base import BaseCommand
from data_collection.ingestion.fec_ingestion import FECIngestion
from data_collection.ingestion.lobbying_ingestion import LobbyingIngestion
from data_collection.ingestion.irs_ingestion import IRSIngestion
from data_collection.ingestion.sec_ingestion import SECIngestion
from data_collection.ingestion.data_processor import DataProcessor
import os


class Command(BaseCommand):
    help = 'Test the data ingestion pipeline with mock data'

    def handle(self, *args, **options):
        self.stdout.write('🧪 Testing data ingestion pipeline...')
        self.stdout.write('=' * 60)
        
        # Check API key status
        self.stdout.write('\n📋 API Key Status:')
        fec_key = os.getenv('FEC_API_KEY', '')
        propublica_key = os.getenv('PROPUBLICA_API_KEY', '')
        sec_key = os.getenv('SEC_API_KEY', '')
        
        self.stdout.write(f"   FEC API: {'✅ Configured' if fec_key and fec_key != 'your_fec_api_key_here' else '⚠️  Not configured'}")
        self.stdout.write(f"   ProPublica API: {'✅ Configured' if propublica_key and propublica_key != 'your_propublica_api_key_here' else '⚠️  Not configured'}")
        self.stdout.write(f"   SEC-API.io: {'✅ Configured' if sec_key and sec_key != 'your_sec_api_key_here' else '⚠️  Not configured'}")
        self.stdout.write(f"   Senate LDA: ✅ Public data (no key required)")
        
        # Test FEC ingestion
        self.stdout.write('\n1. Testing FEC Ingestion...')
        fec_ingestion = FECIngestion()
        fec_data = fec_ingestion.fetch_data(year=2024)
        self.stdout.write(f'   📊 FEC: Retrieved {len(fec_data)} records')
        
        # Test Lobbying ingestion
        self.stdout.write('\n2. Testing Lobbying Ingestion...')
        lobbying_ingestion = LobbyingIngestion()
        lobbying_data = lobbying_ingestion.fetch_data(year=2024)
        self.stdout.write(f'   📊 Lobbying: Retrieved {len(lobbying_data)} records')
        
        # Test IRS ingestion
        self.stdout.write('\n3. Testing IRS Ingestion...')
        irs_ingestion = IRSIngestion()
        irs_data = irs_ingestion.fetch_data(year=2023)
        self.stdout.write(f'   📊 IRS: Retrieved {len(irs_data)} records')
        
        # Test SEC ingestion
        self.stdout.write('\n4. Testing SEC Ingestion...')
        sec_ingestion = SECIngestion()
        sec_data = sec_ingestion.fetch_data(year=2023)
        self.stdout.write(f'   📊 SEC: Retrieved {len(sec_data)} records')
        
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
        
        # Provide next steps
        self.stdout.write('\n📝 Next Steps:')
        self.stdout.write('1. To use real data, add API keys to your .env file:')
        self.stdout.write('   - FEC_API_KEY=your_key_here')
        self.stdout.write('   - PROPUBLICA_API_KEY=your_key_here')
        self.stdout.write('   - SEC_API_KEY=your_key_here')
        self.stdout.write('2. Run: python manage.py create_sample_data')
        self.stdout.write('3. Run: python manage.py ingest_data --dry-run')
        self.stdout.write('4. Run: python manage.py ingest_data')
        
        self.stdout.write('\n💡 Note: The application works with sample data even without API keys!')
