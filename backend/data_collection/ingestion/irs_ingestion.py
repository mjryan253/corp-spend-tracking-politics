import requests
import os
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class IRSIngestion:
    """IRS charitable grants data ingestion with classification."""
    
    def __init__(self):
        self.api_key = os.getenv('PROPUBLICA_API_KEY', '')
        self.base_url = 'https://api.propublica.org/nonprofits/v1'
        self.headers = {
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json'
        }
        
        # Log API key status
        if self.api_key and self.api_key != 'your_propublica_api_key_here':
            print(f"✅ ProPublica API key found: {self.api_key[:8]}...")
        else:
            print("⚠️  ProPublica API key not found or not configured. Using mock data.")
        
        # Classification keywords for different categories
        self.category_keywords = {
            'Religious': [
                'church', 'temple', 'mosque', 'synagogue', 'ministry', 'mission',
                'catholic', 'protestant', 'baptist', 'methodist', 'lutheran',
                'presbyterian', 'episcopal', 'orthodox', 'jewish', 'islamic',
                'hindu', 'buddhist', 'religious', 'faith', 'spiritual',
                'diocese', 'archdiocese', 'parish', 'congregation'
            ],
            'Education': [
                'university', 'college', 'school', 'academy', 'institute',
                'foundation', 'scholarship', 'education', 'learning',
                'research', 'library', 'museum', 'training'
            ],
            'Healthcare': [
                'hospital', 'medical', 'health', 'clinic', 'care',
                'treatment', 'therapy', 'rehabilitation', 'wellness',
                'disease', 'cancer', 'heart', 'mental health'
            ],
            'Humanitarian': [
                'red cross', 'salvation army', 'united way', 'humanitarian',
                'disaster', 'relief', 'emergency', 'aid', 'assistance',
                'charity', 'help', 'support', 'community'
            ],
            'Environment': [
                'environment', 'conservation', 'wildlife', 'nature',
                'climate', 'sustainability', 'green', 'ecology',
                'forest', 'ocean', 'clean', 'renewable'
            ],
            'Arts': [
                'art', 'museum', 'gallery', 'theater', 'theatre',
                'music', 'dance', 'performance', 'cultural',
                'creative', 'arts', 'entertainment'
            ]
        }
    
    def fetch_data(self, year: int = None, ein: str = None) -> List[Dict[str, Any]]:
        """
        Fetch charitable grant data from IRS/ProPublica.
        
        Args:
            year: Year to fetch data for
            ein: Specific EIN to fetch
            
        Returns:
            List of charitable grant records
        """
        if not year:
            year = datetime.now().year
            
        # Check if API key is available and properly configured
        if not self.api_key or self.api_key == 'your_propublica_api_key_here':
            print("📊 Using mock ProPublica data for development/testing")
            return self._get_mock_data(year, ein)
            
        print(f"🔗 Fetching real ProPublica data for year {year}...")
        grants = []
        
        # Get foundation EINs for corporate foundations
        if ein:
            foundation_eins = [ein]
        else:
            foundation_eins = self._get_corporate_foundation_eins()
        
        for foundation_ein in foundation_eins:
            try:
                foundation_grants = self._fetch_foundation_grants(foundation_ein, year)
                grants.extend(foundation_grants)
            except Exception as e:
                print(f"❌ Error fetching grants for foundation {foundation_ein}: {e}")
                continue
        
        # If no real data was fetched, return mock data
        if not grants:
            print("⚠️  No real ProPublica data fetched. Falling back to mock data.")
            return self._get_mock_data(year, ein)
        
        print(f"✅ Successfully fetched {len(grants)} ProPublica records")
        return grants
    
    def _get_corporate_foundation_eins(self) -> List[str]:
        """Get list of corporate foundation EINs."""
        # This would typically query the IRS database for foundation information
        # For now, return some known corporate foundation EINs
        return [
            '13-3398765',  # Example Apple Foundation
            '91-1144442',  # Example Microsoft Foundation
            '94-3068481',  # Example Google Foundation
        ]
    
    def _fetch_foundation_grants(self, foundation_ein: str, year: int) -> List[Dict[str, Any]]:
        """Fetch grants for a specific foundation."""
        url = f"{self.base_url}/organizations/{foundation_ein}/grants"
        
        params = {
            'year': year,
            'limit': 100
        }
        
        grants = []
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = data.get('grants', [])
            
            for grant in results:
                processed_grant = self._process_grant(grant, foundation_ein)
                if processed_grant:
                    grants.append(processed_grant)
            
        except requests.RequestException as e:
            print(f"Error fetching grants for foundation {foundation_ein}: {e}")
        
        return grants
    
    def _process_grant(self, grant: Dict[str, Any], foundation_ein: str) -> Dict[str, Any]:
        """Process a single grant record."""
        try:
            recipient_name = grant.get('recipient_name', '')
            grant_description = grant.get('purpose', '')
            
            # Classify the grant recipient
            category = self._classify_recipient(recipient_name, grant_description)
            
            return {
                'foundation_ein': foundation_ein,
                'recipient_name': recipient_name,
                'recipient_ein': grant.get('recipient_ein'),
                'amount': Decimal(str(grant.get('amount', 0))),
                'fiscal_year': grant.get('fiscal_year'),
                'grant_description': grant_description,
                'recipient_category': category,
                'grant_date': self._parse_date(grant.get('date')),
                'recipient_address': grant.get('recipient_address'),
                'recipient_city': grant.get('recipient_city'),
                'recipient_state': grant.get('recipient_state'),
            }
        except Exception as e:
            print(f"Error processing grant: {e}")
            return None
    
    def _classify_recipient(self, recipient_name: str, description: str) -> str:
        """
        Classify a grant recipient based on name and description.
        
        Args:
            recipient_name: Name of the recipient organization
            description: Description of the grant purpose
            
        Returns:
            Category string (Religious, Education, Healthcare, etc.)
        """
        # Combine name and description for classification
        text = f"{recipient_name} {description}".lower()
        
        # Check each category's keywords
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    return category
        
        # Default category if no match found
        return 'Other'
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object."""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return None
    
    def get_foundation_info(self, ein: str) -> Dict[str, Any]:
        """Get detailed information about a foundation."""
        url = f"{self.base_url}/organizations/{ein}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching foundation info for {ein}: {e}")
            return {}
    
    def search_foundations(self, company_name: str) -> List[Dict[str, Any]]:
        """Search for foundations related to a company."""
        url = f"{self.base_url}/search"
        
        params = {
            'q': f"{company_name} foundation",
            'limit': 10
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('organizations', [])
            
        except requests.RequestException as e:
            print(f"Error searching foundations for {company_name}: {e}")
            return []
    
    def get_grant_statistics(self, foundation_ein: str, year: int = None) -> Dict[str, Any]:
        """Get grant statistics for a foundation."""
        grants = self._fetch_foundation_grants(foundation_ein, year or datetime.now().year)
        
        if not grants:
            return {}
        
        # Calculate statistics
        total_amount = sum(grant['amount'] for grant in grants)
        category_counts = {}
        
        for grant in grants:
            category = grant.get('recipient_category', 'Other')
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return {
            'total_grants': len(grants),
            'total_amount': total_amount,
            'category_breakdown': category_counts,
            'average_grant': total_amount / len(grants) if grants else 0
        }
    
    def _get_mock_data(self, year: int, ein: str = None) -> List[Dict[str, Any]]:
        """Return mock charitable grant data for development/testing."""
        return [
            {
                'foundation_ein': '13-3398765',
                'recipient_name': 'American Red Cross',
                'recipient_ein': '53-0196605',
                'amount': Decimal('1000000'),
                'fiscal_year': year,
                'grant_description': 'Disaster relief and emergency response',
                'recipient_category': 'Humanitarian',
                'grant_date': datetime(year, 6, 15),
                'recipient_address': '431 18th St NW',
                'recipient_city': 'Washington',
                'recipient_state': 'DC',
            },
            {
                'foundation_ein': '91-1144442',
                'recipient_name': 'University of Washington Foundation',
                'recipient_ein': '91-1077680',
                'amount': Decimal('500000'),
                'fiscal_year': year,
                'grant_description': 'Computer science education and research',
                'recipient_category': 'Education',
                'grant_date': datetime(year, 8, 20),
                'recipient_address': '4333 Brooklyn Ave NE',
                'recipient_city': 'Seattle',
                'recipient_state': 'WA',
            },
            {
                'foundation_ein': '94-3068481',
                'recipient_name': 'St. Mary\'s Catholic Church',
                'recipient_ein': '94-3068481',
                'amount': Decimal('250000'),
                'fiscal_year': year,
                'grant_description': 'Community outreach and youth programs',
                'recipient_category': 'Religious',
                'grant_date': datetime(year, 9, 10),
                'recipient_address': '219 8th Ave S',
                'recipient_city': 'Seattle',
                'recipient_state': 'WA',
            },
            {
                'foundation_ein': '13-3398765',
                'recipient_name': 'Stanford University',
                'recipient_ein': '94-1156365',
                'amount': Decimal('750000'),
                'fiscal_year': year,
                'grant_description': 'Technology innovation and research',
                'recipient_category': 'Education',
                'grant_date': datetime(year, 10, 5),
                'recipient_address': '450 Serra Mall',
                'recipient_city': 'Stanford',
                'recipient_state': 'CA',
            }
        ]
