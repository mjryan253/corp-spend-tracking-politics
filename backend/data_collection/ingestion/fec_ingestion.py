import requests
import os
from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class FECIngestion:
    """FEC API ingestion for political contributions."""
    
    def __init__(self):
        self.api_key = os.getenv('FEC_API_KEY', '')
        self.base_url = 'https://api.open.fec.gov/v1'
        self.headers = {
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json'
        }
        
        # Log API key status
        if self.api_key and self.api_key != 'your_fec_api_key_here':
            print(f"✅ FEC API key found: {self.api_key[:8]}...")
        else:
            print("⚠️  FEC API key not found or not configured. Using mock data.")
    
    def fetch_data(self, year: int = None, committee_id: str = None) -> List[Dict[str, Any]]:
        """
        Fetch political contribution data from FEC API.
        
        Args:
            year: Year to fetch data for
            committee_id: Specific committee ID to fetch
            
        Returns:
            List of contribution records
        """
        if not year:
            year = datetime.now().year
            
        # Check if API key is available and properly configured
        if not self.api_key or self.api_key == 'your_fec_api_key_here':
            print("📊 Using mock FEC data for development/testing")
            return self._get_mock_data(year)
            
        print(f"🔗 Fetching real FEC data for year {year}...")
        contributions = []
        
        # Get committee IDs for corporate PACs
        if committee_id:
            committee_ids = [committee_id]
        else:
            committee_ids = self._get_corporate_pac_ids()
        
        for committee_id in committee_ids:
            try:
                committee_contributions = self._fetch_committee_contributions(
                    committee_id, year
                )
                contributions.extend(committee_contributions)
            except Exception as e:
                print(f"❌ Error fetching data for committee {committee_id}: {e}")
                continue
        
        # If no real data was fetched, return mock data
        if not contributions:
            print("⚠️  No real FEC data fetched. Falling back to mock data.")
            return self._get_mock_data(year)
        
        print(f"✅ Successfully fetched {len(contributions)} FEC records")
        return contributions
    
    def _get_corporate_pac_ids(self) -> List[str]:
        """Get list of corporate PAC committee IDs."""
        # This would typically query the FEC API for committee information
        # For now, return some known corporate PAC IDs
        return [
            'C00123456',  # Example Apple PAC
            'C00234567',  # Example Microsoft PAC
            'C00345678',  # Example Google PAC
        ]
    
    def _fetch_committee_contributions(self, committee_id: str, year: int) -> List[Dict[str, Any]]:
        """Fetch contributions for a specific committee."""
        url = f"{self.base_url}/schedules/schedule_a/"
        
        params = {
            'committee_id': committee_id,
            'two_year_transaction_period': year,
            'sort': '-contribution_receipt_date',
            'per_page': 100,
            'page': 1
        }
        
        contributions = []
        
        while True:
            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                results = data.get('results', [])
                
                if not results:
                    break
                
                for contribution in results:
                    processed_contribution = self._process_contribution(contribution)
                    if processed_contribution:
                        contributions.append(processed_contribution)
                
                # Check if there are more pages
                pagination = data.get('pagination', {})
                if pagination.get('page', 1) >= pagination.get('pages', 1):
                    break
                    
                params['page'] += 1
                
            except requests.RequestException as e:
                print(f"Error fetching contributions for committee {committee_id}: {e}")
                break
        
        return contributions
    
    def _process_contribution(self, contribution: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single contribution record."""
        try:
            # Extract relevant fields
            return {
                'committee_id': contribution.get('committee_id'),
                'committee_name': contribution.get('committee_name'),
                'recipient_name': contribution.get('contribution_receipt_date'),
                'recipient_party': contribution.get('contributor_employer'),
                'amount': Decimal(str(contribution.get('contribution_receipt_amount', 0))),
                'date': self._parse_date(contribution.get('contribution_receipt_date')),
                'election_cycle': contribution.get('two_year_transaction_period'),
                'contributor_name': contribution.get('contributor_name'),
                'contributor_employer': contribution.get('contributor_employer'),
                'contributor_occupation': contribution.get('contributor_occupation'),
            }
        except Exception as e:
            print(f"Error processing contribution: {e}")
            return None
    
    def _parse_date(self, date_str: str) -> date:
        """Parse date string to date object."""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return None
    
    def get_committee_info(self, committee_id: str) -> Dict[str, Any]:
        """Get detailed information about a committee."""
        url = f"{self.base_url}/committee/{committee_id}/"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching committee info for {committee_id}: {e}")
            return {}

    def _get_mock_data(self, year: int) -> List[Dict[str, Any]]:
        """Return mock FEC data for development/testing."""
        return [
            {
                'committee_id': 'C00123456',
                'committee_name': 'Apple Inc. PAC',
                'recipient_name': 'Sen. John Smith',
                'recipient_party': 'Democratic',
                'amount': Decimal('5000'),
                'date': date(year, 1, 15),
                'election_cycle': str(year),
                'contributor_name': 'Apple Inc.',
                'contributor_employer': 'Apple Inc.',
                'contributor_occupation': 'Executive',
            },
            {
                'committee_id': 'C00234567',
                'committee_name': 'Microsoft PAC',
                'recipient_name': 'Rep. Jane Doe',
                'recipient_party': 'Republican',
                'amount': Decimal('3500'),
                'date': date(year, 2, 20),
                'election_cycle': str(year),
                'contributor_name': 'Microsoft Corporation',
                'contributor_employer': 'Microsoft Corporation',
                'contributor_occupation': 'Executive',
            },
            {
                'committee_id': 'C00345678',
                'committee_name': 'Alphabet Inc. PAC',
                'recipient_name': 'Sen. Bob Johnson',
                'recipient_party': 'Democratic',
                'amount': Decimal('4500'),
                'date': date(year, 3, 10),
                'election_cycle': str(year),
                'contributor_name': 'Alphabet Inc.',
                'contributor_employer': 'Alphabet Inc.',
                'contributor_occupation': 'Executive',
            }
        ]
