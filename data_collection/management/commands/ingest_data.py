from django.core.management.base import BaseCommand
from django.utils import timezone
from data_collection.ingestion.fec_ingestion import FECIngestion
from data_collection.ingestion.lobbying_ingestion import LobbyingIngestion
from data_collection.ingestion.irs_ingestion import IRSIngestion
from data_collection.ingestion.sec_ingestion import SECIngestion
from data_collection.ingestion.data_processor import DataProcessor


class Command(BaseCommand):
    help = 'Ingest data from all sources: FEC, Senate LDA, IRS, and SEC'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sources',
            nargs='+',
            choices=['fec', 'lobbying', 'irs', 'sec', 'all'],
            default=['all'],
            help='Specify which data sources to ingest'
        )
        parser.add_argument(
            '--year',
            type=int,
            default=timezone.now().year,
            help='Year to ingest data for (default: current year)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without saving data to database'
        )

    def handle(self, *args, **options):
        sources = options['sources']
        year = options['year']
        dry_run = options['dry_run']

        self.stdout.write(f"Starting data ingestion for year {year}")
        if dry_run:
            self.stdout.write("DRY RUN MODE - No data will be saved to database")
        
        # Initialize data processor
        processor = DataProcessor()
        
        # Process each requested source
        if 'all' in sources or 'fec' in sources:
            self.stdout.write("Ingesting FEC political contribution data...")
            fec_ingestion = FECIngestion()
            fec_data = fec_ingestion.fetch_data(year=year)
            if not dry_run:
                processor.process_fec_data(fec_data)
            self.stdout.write(f"FEC: Retrieved {len(fec_data)} records")

        if 'all' in sources or 'lobbying' in sources:
            self.stdout.write("Ingesting Senate LDA lobbying data...")
            lobbying_ingestion = LobbyingIngestion()
            lobbying_data = lobbying_ingestion.fetch_data(year=year)
            if not dry_run:
                processor.process_lobbying_data(lobbying_data)
            self.stdout.write(f"Lobbying: Retrieved {len(lobbying_data)} records")

        if 'all' in sources or 'irs' in sources:
            self.stdout.write("Ingesting IRS charitable grant data...")
            irs_ingestion = IRSIngestion()
            irs_data = irs_ingestion.fetch_data(year=year)
            if not dry_run:
                processor.process_irs_data(irs_data)
            self.stdout.write(f"IRS: Retrieved {len(irs_data)} records")

        if 'all' in sources or 'sec' in sources:
            self.stdout.write("Ingesting SEC financial data...")
            sec_ingestion = SECIngestion()
            sec_data = sec_ingestion.fetch_data(year=year)
            if not dry_run:
                processor.process_sec_data(sec_data)
            self.stdout.write(f"SEC: Retrieved {len(sec_data)} records")

        self.stdout.write(
            self.style.SUCCESS('Data ingestion completed successfully!')
        )
