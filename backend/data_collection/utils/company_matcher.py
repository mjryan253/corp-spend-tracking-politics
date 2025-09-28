"""
Enhanced company name matching system using fuzzy matching algorithms.
Replaces the fragile string matching approach with robust fuzzy matching.
"""
from difflib import SequenceMatcher
from typing import List, Tuple, Optional, Dict, Any
import re
from django.db.models import Q
from ..models import Company


class CompanyMatcher:
    """
    Advanced company name matching system using multiple algorithms.
    Provides confidence scoring and handles various name variations.
    """
    
    def __init__(self, match_threshold: int = 85):
        """
        Initialize the company matcher.
        
        Args:
            match_threshold: Minimum confidence score for a match (0-100)
        """
        self.match_threshold = match_threshold
        self.company_cache = {}
        self._load_company_cache()
    
    def _load_company_cache(self):
        """Load all companies into cache for faster matching."""
        companies = Company.objects.all()
        for company in companies:
            normalized_name = self._normalize_company_name(company.name)
            self.company_cache[normalized_name] = company
    
    def _normalize_company_name(self, name: str) -> str:
        """
        Normalize company names for better matching.
        
        Args:
            name: Company name to normalize
            
        Returns:
            Normalized company name
        """
        if not name:
            return ""
        
        # Remove common suffixes and variations
        suffixes = [
            'Inc', 'Corp', 'Corporation', 'LLC', 'Ltd', 'Limited', 
            'Company', 'Co', 'LP', 'LLP', 'Group', 'Holdings',
            'Enterprises', 'International', 'Global', 'Systems',
            'Technologies', 'Solutions', 'Services', 'Partners'
        ]
        
        # Create regex pattern for suffixes
        suffix_pattern = r'\b(' + '|'.join(suffixes) + r')\b'
        name = re.sub(suffix_pattern, '', name, flags=re.IGNORECASE)
        
        # Remove special characters and normalize whitespace
        name = re.sub(r'[^\w\s]', ' ', name)
        name = re.sub(r'\s+', ' ', name)
        
        # Remove common words that don't help with matching
        common_words = ['the', 'and', 'of', 'for', 'in', 'on', 'at', 'to']
        words = name.split()
        words = [word for word in words if word.lower() not in common_words]
        
        return ' '.join(words).lower().strip()
    
    def _calculate_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate similarity between two names using multiple algorithms.
        
        Args:
            name1: First name
            name2: Second name
            
        Returns:
            Similarity score (0-100)
        """
        # Normalize both names
        norm1 = self._normalize_company_name(name1)
        norm2 = self._normalize_company_name(name2)
        
        if not norm1 or not norm2:
            return 0.0
        
        # Exact match
        if norm1 == norm2:
            return 100.0
        
        # Sequence matcher similarity
        seq_similarity = SequenceMatcher(None, norm1, norm2).ratio() * 100
        
        # Token-based similarity (order independent)
        tokens1 = set(norm1.split())
        tokens2 = set(norm2.split())
        
        if not tokens1 or not tokens2:
            return 0.0
        
        # Jaccard similarity
        intersection = len(tokens1.intersection(tokens2))
        union = len(tokens1.union(tokens2))
        jaccard_similarity = (intersection / union) * 100 if union > 0 else 0
        
        # Weighted average of different similarity measures
        weighted_score = (seq_similarity * 0.6) + (jaccard_similarity * 0.4)
        
        return weighted_score
    
    def find_best_match(self, pac_name: str, companies: List[Company] = None) -> Tuple[Optional[Company], float]:
        """
        Find the best company match for a PAC name.
        
        Args:
            pac_name: PAC name to match
            companies: Optional list of companies to search in
            
        Returns:
            Tuple of (best_match_company, confidence_score)
        """
        if not pac_name:
            return None, 0.0
        
        # Use provided companies or all companies
        if companies is None:
            companies = list(Company.objects.all())
        
        best_match = None
        best_score = 0.0
        
        for company in companies:
            similarity = self._calculate_similarity(pac_name, company.name)
            
            if similarity > best_score and similarity >= self.match_threshold:
                best_score = similarity
                best_match = company
        
        return best_match, best_score
    
    def find_multiple_matches(self, pac_name: str, limit: int = 5) -> List[Tuple[Company, float]]:
        """
        Find multiple potential matches for a PAC name.
        
        Args:
            pac_name: PAC name to match
            limit: Maximum number of matches to return
            
        Returns:
            List of (company, confidence_score) tuples
        """
        if not pac_name:
            return []
        
        companies = list(Company.objects.all())
        matches = []
        
        for company in companies:
            similarity = self._calculate_similarity(pac_name, company.name)
            
            if similarity >= self.match_threshold:
                matches.append((company, similarity))
        
        # Sort by confidence score (highest first)
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches[:limit]
    
    def match_political_contributions(self) -> Dict[str, Any]:
        """
        Match all political contributions to companies.
        
        Returns:
            Dictionary with matching statistics
        """
        from ..models import PoliticalContribution
        
        contributions = PoliticalContribution.objects.all()
        matches = []
        unmatched = []
        
        for contribution in contributions:
            pac_name = contribution.company_pac_id
            best_match, confidence = self.find_best_match(pac_name)
            
            if best_match:
                matches.append({
                    'contribution_id': contribution.id,
                    'pac_name': pac_name,
                    'matched_company': best_match.name,
                    'confidence': confidence
                })
            else:
                unmatched.append({
                    'contribution_id': contribution.id,
                    'pac_name': pac_name
                })
        
        return {
            'total_contributions': len(contributions),
            'matched': len(matches),
            'unmatched': len(unmatched),
            'match_rate': len(matches) / len(contributions) if contributions else 0,
            'matches': matches,
            'unmatched': unmatched
        }
    
    def get_matching_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about company matching performance.
        
        Returns:
            Dictionary with matching statistics
        """
        from ..models import PoliticalContribution
        
        total_contributions = PoliticalContribution.objects.count()
        unique_pacs = PoliticalContribution.objects.values('company_pac_id').distinct().count()
        
        # Sample some PACs for matching analysis
        sample_pacs = PoliticalContribution.objects.values_list('company_pac_id', flat=True).distinct()[:100]
        
        high_confidence_matches = 0
        medium_confidence_matches = 0
        low_confidence_matches = 0
        no_matches = 0
        
        for pac_name in sample_pacs:
            best_match, confidence = self.find_best_match(pac_name)
            
            if confidence >= 90:
                high_confidence_matches += 1
            elif confidence >= 70:
                medium_confidence_matches += 1
            elif confidence >= 50:
                low_confidence_matches += 1
            else:
                no_matches += 1
        
        return {
            'total_contributions': total_contributions,
            'unique_pacs': unique_pacs,
            'sample_size': len(sample_pacs),
            'high_confidence_matches': high_confidence_matches,
            'medium_confidence_matches': medium_confidence_matches,
            'low_confidence_matches': low_confidence_matches,
            'no_matches': no_matches,
            'overall_match_rate': (high_confidence_matches + medium_confidence_matches) / len(sample_pacs) if sample_pacs else 0
        }


# Global instance for easy access
company_matcher = CompanyMatcher()


def get_company_for_pac(pac_name: str) -> Optional[Company]:
    """
    Convenience function to get company for a PAC name.
    
    Args:
        pac_name: PAC name to match
        
    Returns:
        Matched company or None
    """
    company, _ = company_matcher.find_best_match(pac_name)
    return company


def get_company_matches_for_pac(pac_name: str, limit: int = 5) -> List[Tuple[Company, float]]:
    """
    Convenience function to get multiple company matches for a PAC name.
    
    Args:
        pac_name: PAC name to match
        limit: Maximum number of matches to return
        
    Returns:
        List of (company, confidence_score) tuples
    """
    return company_matcher.find_multiple_matches(pac_name, limit)
