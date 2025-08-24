import requests
import xml.etree.ElementTree as ET
import os
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class LobbyingIngestion:
    """Senate LDA lobbying data ingestion."""
    
    def __init__(self):
        self.base_url = 'https://lda.senate.gov/api/v1'
        self.headers = {
            'Content-Type': 'application/json'
        }
    
    def fetch_data(self, year: int = None, quarter: int = None) -> List[Dict[str, Any]]:
        """
        Fetch lobbying data from Senate LDA.
        
        Args:
            year: Year to fetch data for
            quarter: Quarter to fetch data for (1-4)
            
        Returns:
            List of lobbying report records
        """
        if not year:
            year = datetime.now().year
            
        lobbying_reports = []
        
        # Fetch data for specified quarter or all quarters
        quarters = [quarter] if quarter else [1, 2, 3, 4]
        
        for q in quarters:
            try:
                quarter_data = self._fetch_quarter_data(year, q)
                lobbying_reports.extend(quarter_data)
            except Exception as e:
                print(f"Error fetching lobbying data for {year} Q{q}: {e}")
                continue
        
        return lobbying_reports
    
    def _fetch_quarter_data(self, year: int, quarter: int) -> List[Dict[str, Any]]:
        """Fetch lobbying data for a specific quarter."""
        # The Senate LDA API endpoint structure
        url = f"{self.base_url}/reports"
        
        params = {
            'year': year,
            'quarter': quarter,
            'format': 'json',
            'limit': 1000
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            reports = data.get('results', [])
            
            processed_reports = []
            for report in reports:
                processed_report = self._process_lobbying_report(report)
                if processed_report:
                    processed_reports.append(processed_report)
            
            return processed_reports
            
        except requests.RequestException as e:
            print(f"Error fetching lobbying data for {year} Q{quarter}: {e}")
            return []
    
    def _process_lobbying_report(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single lobbying report."""
        try:
            # Extract lobbying firm and client information
            registrant = report.get('registrant', {})
            client = report.get('client', {})
            
            # Get lobbying activities
            activities = report.get('lobbying_activities', [])
            issues = []
            for activity in activities:
                issue = activity.get('general_issue_area', '')
                if issue:
                    issues.append(issue)
            
            return {
                'registrant_name': registrant.get('name'),
                'client_name': client.get('name'),
                'year': report.get('year'),
                'quarter': report.get('quarter'),
                'amount_spent': self._parse_amount(report.get('amount')),
                'specific_issues': '; '.join(issues),
                'report_url': report.get('url'),
                'registrant_id': registrant.get('id'),
                'client_id': client.get('id'),
                'report_id': report.get('id'),
                'filing_date': self._parse_date(report.get('filing_date')),
                'lobbyists': self._extract_lobbyists(report.get('lobbyists', [])),
            }
        except Exception as e:
            print(f"Error processing lobbying report: {e}")
            return None
    
    def _parse_amount(self, amount_str: str) -> Decimal:
        """Parse amount string to Decimal."""
        if not amount_str:
            return Decimal('0')
        try:
            # Remove currency symbols and commas
            cleaned = amount_str.replace('$', '').replace(',', '')
            return Decimal(cleaned)
        except (ValueError, TypeError):
            return Decimal('0')
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object."""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return None
    
    def _extract_lobbyists(self, lobbyists_data: List[Dict[str, Any]]) -> List[str]:
        """Extract lobbyist names from lobbying data."""
        names = []
        for lobbyist in lobbyists_data:
            name = lobbyist.get('name')
            if name:
                names.append(name)
        return names
    
    def fetch_company_lobbying(self, company_name: str, year: int = None) -> List[Dict[str, Any]]:
        """Fetch lobbying data for a specific company."""
        if not year:
            year = datetime.now().year
            
        url = f"{self.base_url}/search"
        
        params = {
            'q': company_name,
            'year': year,
            'format': 'json'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = data.get('results', [])
            
            processed_results = []
            for result in results:
                processed_result = self._process_lobbying_report(result)
                if processed_result:
                    processed_results.append(processed_result)
            
            return processed_results
            
        except requests.RequestException as e:
            print(f"Error searching lobbying data for {company_name}: {e}")
            return []
    
    def get_registrant_info(self, registrant_id: str) -> Dict[str, Any]:
        """Get detailed information about a lobbying registrant."""
        url = f"{self.base_url}/registrants/{registrant_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching registrant info for {registrant_id}: {e}")
            return {}
