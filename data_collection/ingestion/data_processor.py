from django.db import transaction
from typing import List, Dict, Any
from data_collection.models import (
    Company, FinancialSummary, LobbyingReport, 
    PoliticalContribution, CharitableGrant
)
from decimal import Decimal
import re


class DataProcessor:
    """Process and link data from multiple sources."""
    
    def __init__(self):
        self.company_mapping = self._load_company_mapping()
    
    def _load_company_mapping(self) -> Dict[str, str]:
        """Load mapping of company names to standardized names."""
        # This would typically load from a configuration file or database
        # For now, return a simple mapping
        return {
            'apple inc': 'Apple Inc.',
            'apple computer': 'Apple Inc.',
            'microsoft corporation': 'Microsoft Corporation',
            'microsoft corp': 'Microsoft Corporation',
            'alphabet inc': 'Alphabet Inc.',
            'google inc': 'Alphabet Inc.',
            'google llc': 'Alphabet Inc.',
        }
    
    def _normalize_company_name(self, name: str) -> str:
        """Normalize company name for matching."""
        if not name:
            return ''
        
        # Convert to lowercase and remove common suffixes
        normalized = name.lower().strip()
        normalized = re.sub(r'\s+(inc|corp|corporation|llc|ltd|limited|company|co)\.?$', '', normalized)
        normalized = re.sub(r'[^\w\s]', '', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def _find_or_create_company(self, name: str, ticker: str = None, cik: str = None) -> Company:
        """Find existing company or create new one."""
        normalized_name = self._normalize_company_name(name)
        
        # Check if we have a mapping for this name
        if normalized_name in self.company_mapping:
            name = self.company_mapping[normalized_name]
        
        # Try to find by name
        company = Company.objects.filter(name__iexact=name).first()
        
        if not company and ticker:
            # Try to find by ticker
            company = Company.objects.filter(ticker__iexact=ticker).first()
        
        if not company and cik:
            # Try to find by CIK
            company = Company.objects.filter(cik=cik).first()
        
        if not company:
            # Create new company
            company = Company.objects.create(
                name=name,
                ticker=ticker,
                cik=cik
            )
        
        return company
    
    @transaction.atomic
    def process_fec_data(self, fec_data: List[Dict[str, Any]]) -> None:
        """Process FEC political contribution data."""
        for contribution in fec_data:
            try:
                # Extract company name from PAC name
                pac_name = contribution.get('committee_name', '')
                company_name = self._extract_company_from_pac(pac_name)
                
                if not company_name:
                    continue
                
                # Find or create company
                company = self._find_or_create_company(company_name)
                
                # Create political contribution record
                PoliticalContribution.objects.create(
                    company_pac_id=contribution.get('committee_name', ''),
                    recipient_name=contribution.get('recipient_name', ''),
                    recipient_party=contribution.get('recipient_party', ''),
                    amount=contribution.get('amount', Decimal('0')),
                    date=contribution.get('date'),
                    election_cycle=contribution.get('election_cycle', ''),
                )
                
            except Exception as e:
                print(f"Error processing FEC contribution: {e}")
                continue
    
    def _extract_company_from_pac(self, pac_name: str) -> str:
        """Extract company name from PAC name."""
        if not pac_name:
            return ''
        
        # Common patterns for corporate PAC names
        patterns = [
            r'(.+?)\s+PAC',
            r'(.+?)\s+POLITICAL\s+ACTION\s+COMMITTEE',
            r'(.+?)\s+COMMITTEE',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, pac_name, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return pac_name
    
    @transaction.atomic
    def process_lobbying_data(self, lobbying_data: List[Dict[str, Any]]) -> None:
        """Process Senate LDA lobbying data."""
        for report in lobbying_data:
            try:
                # Extract company name from client name
                client_name = report.get('client_name', '')
                company_name = self._normalize_company_name(client_name)
                
                if not company_name:
                    continue
                
                # Find or create company
                company = self._find_or_create_company(client_name)
                
                # Create lobbying report record
                LobbyingReport.objects.create(
                    company=company,
                    year=report.get('year'),
                    quarter=report.get('quarter'),
                    amount_spent=report.get('amount_spent', Decimal('0')),
                    specific_issues=report.get('specific_issues', ''),
                    report_url=report.get('report_url', ''),
                )
                
            except Exception as e:
                print(f"Error processing lobbying report: {e}")
                continue
    
    @transaction.atomic
    def process_irs_data(self, irs_data: List[Dict[str, Any]]) -> None:
        """Process IRS charitable grant data."""
        for grant in irs_data:
            try:
                # Extract company name from foundation EIN or name
                foundation_ein = grant.get('foundation_ein', '')
                company_name = self._get_company_from_foundation(foundation_ein)
                
                if not company_name:
                    continue
                
                # Find or create company
                company = self._find_or_create_company(company_name)
                
                # Create charitable grant record
                CharitableGrant.objects.create(
                    company=company,
                    recipient_name=grant.get('recipient_name', ''),
                    recipient_ein=grant.get('recipient_ein', ''),
                    amount=grant.get('amount', Decimal('0')),
                    fiscal_year=grant.get('fiscal_year'),
                    grant_description=grant.get('grant_description', ''),
                    recipient_category=grant.get('recipient_category', ''),
                )
                
            except Exception as e:
                print(f"Error processing IRS grant: {e}")
                continue
    
    def _get_company_from_foundation(self, foundation_ein: str) -> str:
        """Get company name from foundation EIN."""
        # This would typically query a database or use a mapping
        # For now, return a simple mapping
        foundation_mapping = {
            '13-3398765': 'Apple Inc.',
            '91-1144442': 'Microsoft Corporation',
            '94-3068481': 'Alphabet Inc.',
        }
        
        return foundation_mapping.get(foundation_ein, '')
    
    @transaction.atomic
    def process_sec_data(self, sec_data: List[Dict[str, Any]]) -> None:
        """Process SEC financial data."""
        for financial in sec_data:
            try:
                company_name = financial.get('company_name', '')
                cik = financial.get('cik', '')
                ticker = financial.get('ticker', '')
                
                if not company_name:
                    continue
                
                # Find or create company
                company = self._find_or_create_company(company_name, ticker, cik)
                
                # Update company information if we have new data
                if cik and not company.cik:
                    company.cik = cik
                if ticker and not company.ticker:
                    company.ticker = ticker
                company.save()
                
                # Create or update financial summary
                fiscal_year = financial.get('fiscal_year')
                if fiscal_year:
                    financial_summary, created = FinancialSummary.objects.get_or_create(
                        company=company,
                        fiscal_year=fiscal_year,
                        defaults={
                            'total_revenue': financial.get('total_revenue'),
                            'net_income': financial.get('net_income'),
                        }
                    )
                    
                    if not created:
                        # Update existing record
                        financial_summary.total_revenue = financial.get('total_revenue')
                        financial_summary.net_income = financial.get('net_income')
                        financial_summary.save()
                
            except Exception as e:
                print(f"Error processing SEC financial data: {e}")
                continue
    
    def link_companies_across_sources(self) -> Dict[str, Any]:
        """Link companies across different data sources."""
        companies = Company.objects.all()
        linking_results = {
            'total_companies': companies.count(),
            'linked_companies': 0,
            'unlinked_companies': 0,
            'details': []
        }
        
        for company in companies:
            # Check if company has data from multiple sources
            has_lobbying = company.lobbying_reports.exists()
            has_charitable = company.charitable_grants.exists()
            has_financial = company.financial_summaries.exists()
            
            # Check for political contributions (by PAC name)
            pac_contributions = PoliticalContribution.objects.filter(
                company_pac_id__icontains=company.name.split()[0]
            )
            has_political = pac_contributions.exists()
            
            if has_lobbying or has_charitable or has_financial or has_political:
                linking_results['linked_companies'] += 1
                linking_results['details'].append({
                    'company': company.name,
                    'lobbying': has_lobbying,
                    'charitable': has_charitable,
                    'financial': has_financial,
                    'political': has_political,
                })
            else:
                linking_results['unlinked_companies'] += 1
        
        return linking_results
    
    def get_data_quality_report(self) -> Dict[str, Any]:
        """Generate a data quality report."""
        report = {
            'companies': {
                'total': Company.objects.count(),
                'with_cik': Company.objects.filter(cik__isnull=False).count(),
                'with_ticker': Company.objects.filter(ticker__isnull=False).count(),
            },
            'financial_summaries': {
                'total': FinancialSummary.objects.count(),
                'with_revenue': FinancialSummary.objects.filter(total_revenue__isnull=False).count(),
                'with_income': FinancialSummary.objects.filter(net_income__isnull=False).count(),
            },
            'lobbying_reports': {
                'total': LobbyingReport.objects.count(),
                'with_amount': LobbyingReport.objects.filter(amount_spent__isnull=False).count(),
            },
            'charitable_grants': {
                'total': CharitableGrant.objects.count(),
                'with_category': CharitableGrant.objects.filter(recipient_category__isnull=False).count(),
            },
            'political_contributions': {
                'total': PoliticalContribution.objects.count(),
                'with_amount': PoliticalContribution.objects.filter(amount__isnull=False).count(),
            }
        }
        
        return report
