import requests
import os
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class SECIngestion:
    """SEC financial data ingestion via SEC-API.io."""
    
    def __init__(self):
        self.api_key = os.getenv('SEC_API_KEY', '')
        self.base_url = 'https://api.sec-api.io'
        self.headers = {
            'Authorization': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def fetch_data(self, year: int = None, cik: str = None) -> List[Dict[str, Any]]:
        """
        Fetch financial data from SEC EDGAR.
        
        Args:
            year: Year to fetch data for
            cik: Specific CIK to fetch
            
        Returns:
            List of financial summary records
        """
        if not year:
            year = datetime.now().year
            
        financial_data = []
        
        # Get company CIKs to fetch
        if cik:
            company_ciks = [cik]
        else:
            company_ciks = self._get_company_ciks()
        
        for company_cik in company_ciks:
            try:
                company_financials = self._fetch_company_financials(company_cik, year)
                if company_financials:
                    financial_data.append(company_financials)
            except Exception as e:
                print(f"Error fetching financial data for CIK {company_cik}: {e}")
                continue
        
        return financial_data
    
    def _get_company_ciks(self) -> List[str]:
        """Get list of company CIKs to fetch financial data for."""
        # This would typically query a database or configuration file
        # For now, return some known company CIKs
        return [
            '0000320193',  # Apple Inc.
            '0000789019',  # Microsoft Corporation
            '0001652044',  # Alphabet Inc.
        ]
    
    def _fetch_company_financials(self, cik: str, year: int) -> Dict[str, Any]:
        """Fetch financial data for a specific company."""
        # Query for 10-K filings for the specified year
        query = {
            "query": {
                "query_string": {
                    "query": f"cik:{cik} AND formType:\"10-K\" AND NOT formType:\"10-K/A\" AND filedAt:[{year}-01-01 TO {year}-12-31]"
                }
            },
            "from": "0",
            "size": "10",
            "sort": [{"filedAt": {"order": "desc"}}]
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/query",
                headers=self.headers,
                json=query
            )
            response.raise_for_status()
            
            data = response.json()
            filings = data.get('filings', [])
            
            if not filings:
                return None
            
            # Get the most recent 10-K filing
            latest_filing = filings[0]
            
            # Extract financial data from the filing
            financial_data = self._extract_financial_data(latest_filing, cik, year)
            
            return financial_data
            
        except requests.RequestException as e:
            print(f"Error fetching financial data for CIK {cik}: {e}")
            return None
    
    def _extract_financial_data(self, filing: Dict[str, Any], cik: str, year: int) -> Dict[str, Any]:
        """Extract financial data from a 10-K filing."""
        try:
            # Get company information
            company_info = self._get_company_info(cik)
            
            # Extract key financial metrics
            financial_metrics = self._extract_financial_metrics(filing)
            
            return {
                'cik': cik,
                'company_name': company_info.get('name', ''),
                'ticker': company_info.get('ticker', ''),
                'fiscal_year': year,
                'total_revenue': financial_metrics.get('total_revenue'),
                'net_income': financial_metrics.get('net_income'),
                'filing_date': filing.get('filedAt'),
                'filing_url': filing.get('linkToFilingDetails'),
                'form_type': filing.get('formType'),
                'accession_number': filing.get('accessionNumber'),
            }
            
        except Exception as e:
            print(f"Error extracting financial data: {e}")
            return None
    
    def _get_company_info(self, cik: str) -> Dict[str, Any]:
        """Get basic company information."""
        query = {
            "query": {
                "query_string": {
                    "query": f"cik:{cik}"
                }
            },
            "from": "0",
            "size": "1"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/query",
                headers=self.headers,
                json=query
            )
            response.raise_for_status()
            
            data = response.json()
            filings = data.get('filings', [])
            
            if filings:
                filing = filings[0]
                return {
                    'name': filing.get('companyName', ''),
                    'ticker': filing.get('ticker', ''),
                    'cik': cik
                }
            
        except requests.RequestException as e:
            print(f"Error fetching company info for CIK {cik}: {e}")
        
        return {'name': '', 'ticker': '', 'cik': cik}
    
    def _extract_financial_metrics(self, filing: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key financial metrics from filing data."""
        # This is a simplified extraction - in practice, you'd parse the actual filing content
        # For now, return placeholder data
        return {
            'total_revenue': Decimal('1000000000'),  # Placeholder
            'net_income': Decimal('100000000'),      # Placeholder
        }
    
    def search_companies(self, company_name: str) -> List[Dict[str, Any]]:
        """Search for companies by name."""
        query = {
            "query": {
                "query_string": {
                    "query": f"companyName:\"{company_name}\""
                }
            },
            "from": "0",
            "size": "10"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/query",
                headers=self.headers,
                json=query
            )
            response.raise_for_status()
            
            data = response.json()
            filings = data.get('filings', [])
            
            companies = []
            seen_ciks = set()
            
            for filing in filings:
                cik = filing.get('cik')
                if cik and cik not in seen_ciks:
                    companies.append({
                        'cik': cik,
                        'name': filing.get('companyName', ''),
                        'ticker': filing.get('ticker', ''),
                    })
                    seen_ciks.add(cik)
            
            return companies
            
        except requests.RequestException as e:
            print(f"Error searching companies for {company_name}: {e}")
            return []
    
    def get_filing_history(self, cik: str, form_type: str = "10-K", years: int = 5) -> List[Dict[str, Any]]:
        """Get filing history for a company."""
        current_year = datetime.now().year
        start_year = current_year - years
        
        query = {
            "query": {
                "query_string": {
                    "query": f"cik:{cik} AND formType:\"{form_type}\" AND filedAt:[{start_year}-01-01 TO {current_year}-12-31]"
                }
            },
            "from": "0",
            "size": "50",
            "sort": [{"filedAt": {"order": "desc"}}]
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/query",
                headers=self.headers,
                json=query
            )
            response.raise_for_status()
            
            data = response.json()
            filings = data.get('filings', [])
            
            return filings
            
        except requests.RequestException as e:
            print(f"Error fetching filing history for CIK {cik}: {e}")
            return []
    
    def get_financial_ratios(self, cik: str, year: int) -> Dict[str, Any]:
        """Calculate financial ratios for a company."""
        financial_data = self._fetch_company_financials(cik, year)
        
        if not financial_data:
            return {}
        
        revenue = financial_data.get('total_revenue', Decimal('0'))
        net_income = financial_data.get('net_income', Decimal('0'))
        
        if revenue and revenue > 0:
            profit_margin = (net_income / revenue) * 100
        else:
            profit_margin = 0
        
        return {
            'profit_margin_percent': float(profit_margin),
            'revenue': float(revenue) if revenue else 0,
            'net_income': float(net_income) if net_income else 0,
            'fiscal_year': year
        }
