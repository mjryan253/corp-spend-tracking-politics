from django.core.management.base import BaseCommand
from django.core.management import call_command
import json
import os


class Command(BaseCommand):
    help = 'Generate OpenAPI schema for the API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='api_schema.json',
            help='Output file path for the schema (default: api_schema.json)'
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['openapi', 'openapi-json'],
            default='openapi-json',
            help='Output format (default: openapi-json)'
        )

    def handle(self, *args, **options):
        output_file = options['output']
        output_format = options['format']
        
        self.stdout.write(
            self.style.SUCCESS('Generating OpenAPI schema...')
        )
        
        try:
            # Use Django's built-in command to generate schema
            call_command(
                'spectacular',
                '--file', output_file,
                '--format', output_format,
                verbosity=1
            )
            
            if os.path.exists(output_file):
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Schema generated successfully: {output_file}'
                    )
                )
                
                # Show some stats about the generated schema
                if output_format == 'openapi-json':
                    with open(output_file, 'r') as f:
                        schema = json.load(f)
                    
                    paths = schema.get('paths', {})
                    components = schema.get('components', {})
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'📊 Schema Statistics:\n'
                            f'   - API Endpoints: {len(paths)}\n'
                            f'   - Components: {len(components.get("schemas", {}))}\n'
                            f'   - Tags: {len(schema.get("tags", []))}'
                        )
                    )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Schema file was not created')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error generating schema: {str(e)}')
            )
