import requests
import os
import logging
from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict, Any
from dotenv import load_dotenv
from .error_handler import (
    robust_api_request, retry_on_failure, log_api_metrics, 
    track_api_calls, circuit_breaker, APIError, RateLimitError,
    api_counter
)

load_dotenv()
logger = logging.getLogger(__name__)


class FECIngestion:
    """FEC API ingestion for political contributions."""
    
    def __init__(self):
        self.api_key = os.getenv('FEC_API_KEY', '')
        self.base_url = 'https://api.open.fec.gov/v1'
        self.headers = {
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json'
        }
        
        # Initialize statistics
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'records_processed': 0,
            'errors': []
        }
        
        # Log API key status
        if self.api_key and self.api_key != 'your_fec_api_key_here':
            logger.info(f"✅ FEC API key found: {self.api_key[:8]}...")
        else:
            logger.warning("⚠️  FEC API key not found or not configured. Using mock data.")
    
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
            logger.info("📊 Using mock FEC data for development/testing")
            return self._get_mock_data(year)
            
        logger.info(f"🔗 Fetching real FEC data for year {year}...")
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
                self.stats['successful_requests'] += 1
            except Exception as e:
                error_msg = f"Error fetching data for committee {committee_id}: {e}"
                logger.error(f"❌ {error_msg}")
                self.stats['failed_requests'] += 1
                self.stats['errors'].append(error_msg)
                continue
        
        self.stats['records_processed'] = len(contributions)
        
        # If no real data was fetched, return mock data
        if not contributions:
            logger.warning("⚠️  No real FEC data fetched. Falling back to mock data.")
            return self._get_mock_data(year)
        
        logger.info(f"✅ Successfully fetched {len(contributions)} FEC records")
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
    
    @retry_on_failure
    @log_api_metrics
    @track_api_calls('fec_committee_contributions')
    @circuit_breaker(failure_threshold=3, recovery_timeout=300)
    def _fetch_committee_contributions(self, committee_id: str, year: int) -> List[Dict[str, Any]]:
        """Fetch contributions for a specific committee with robust error handling."""
        url = f"{self.base_url}/schedules/schedule_a/"
        
        params = {
            'committee_id': committee_id,
            'two_year_transaction_period': year,
            'sort': '-contribution_receipt_date',
            'per_page': 100,
            'page': 1
        }
        
        contributions = []
        max_pages = 50  # Limit to prevent runaway pagination
        
        while params['page'] <= max_pages:
            try:
                self.stats['total_requests'] += 1
                
                response = robust_api_request(
                    url=url,
                    method='GET',
                    headers=self.headers,
                    params=params,
                    timeout=30,
                    max_retries=3
                )
                
                data = response.json()
                results = data.get('results', [])
                
                if not results:
                    logger.info(f"No more results for committee {committee_id} at page {params['page']}")
                    break
                
                for contribution in results:
                    processed_contribution = self._process_contribution(contribution)
                    if processed_contribution:
                        contributions.append(processed_contribution)
                
                # Check if there are more pages
                pagination = data.get('pagination', {})
                total_pages = pagination.get('pages', 1)
                current_page = pagination.get('page', 1)
                
                logger.debug(f"Processed page {current_page}/{total_pages} for committee {committee_id}")
                
                if current_page >= total_pages:
                    break
                    
                params['page'] += 1
                
            except (APIError, RateLimitError) as e:
                logger.error(f"API error fetching contributions for committee {committee_id}: {e}")
                # Let the retry decorator handle retries
                raise
            except Exception as e:
                logger.error(f"Unexpected error fetching contributions for committee {committee_id}: {e}")
                break
        
        logger.info(f"Fetched {len(contributions)} contributions for committee {committee_id}")
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
    
    @retry_on_failure
    @log_api_metrics
    @track_api_calls('fec_committee_info')
    def get_committee_info(self, committee_id: str) -> Dict[str, Any]:
        """Get detailed information about a committee with robust error handling."""
        url = f"{self.base_url}/committee/{committee_id}/"
        
        try:
            response = robust_api_request(
                url=url,
                method='GET',
                headers=self.headers,
                timeout=30,
                max_retries=2
            )
            return response.json()
        except (APIError, RateLimitError) as e:
            logger.error(f"API error fetching committee info for {committee_id}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error fetching committee info for {committee_id}: {e}")
            return {}
    
    def get_ingestion_stats(self) -> Dict[str, Any]:
        """Get ingestion statistics."""
        global_stats = api_counter.get_stats()
        return {
            'fec_specific': self.stats,
            'global_api_stats': global_stats,
            'success_rate': (
                self.stats['successful_requests'] / max(self.stats['total_requests'], 1) * 100
                if self.stats['total_requests'] > 0 else 0
            )
        }
    
    def reset_stats(self):
        """Reset ingestion statistics."""
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'records_processed': 0,
            'errors': []
        }

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
