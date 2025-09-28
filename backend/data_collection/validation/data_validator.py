"""
Comprehensive data validation framework for the Corporate Spending Tracker.
Validates incoming data from external APIs and ensures data quality.
"""
from decimal import Decimal, InvalidOperation
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Union
import re
from django.core.exceptions import ValidationError


class ValidationResult:
    """Container for validation results."""
    
    def __init__(self, valid: bool = True, errors: List[str] = None, warnings: List[str] = None):
        self.valid = valid
        self.errors = errors or []
        self.warnings = warnings or []
    
    def add_error(self, error: str):
        """Add an error message."""
        self.errors.append(error)
        self.valid = False
    
    def add_warning(self, warning: str):
        """Add a warning message."""
        self.warnings.append(warning)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'valid': self.valid,
            'errors': self.errors,
            'warnings': self.warnings,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings)
        }


class DataValidator:
    """
    Comprehensive data validator for all data types in the system.
    Provides validation for companies, lobbying reports, political contributions, and charitable grants.
    """
    
    def __init__(self):
        self.validation_rules = {
            'company': self._validate_company,
            'lobbying': self._validate_lobbying,
            'political': self._validate_political,
            'charitable': self._validate_charitable,
            'financial': self._validate_financial
        }
        
        # Common validation patterns
        self.patterns = {
            'cik': re.compile(r'^\d{10}$'),
            'ticker': re.compile(r'^[A-Z]{1,5}$'),
            'ein': re.compile(r'^\d{2}-?\d{7}$'),
            'email': re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
            'url': re.compile(r'^https?://[^\s/$.?#].[^\s]*$')
        }
    
    def validate_data(self, data_type: str, data: Dict[str, Any]) -> ValidationResult:
        """
        Validate data based on type.
        
        Args:
            data_type: Type of data to validate
            data: Data dictionary to validate
            
        Returns:
            ValidationResult object with validation results
        """
        validator = self.validation_rules.get(data_type)
        if not validator:
            result = ValidationResult(valid=False)
            result.add_error(f'Unknown data type: {data_type}')
            return result
        
        try:
            return validator(data)
        except Exception as e:
            result = ValidationResult(valid=False)
            result.add_error(f'Validation error: {str(e)}')
            return result
    
    def _validate_company(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate company data."""
        result = ValidationResult()
        
        # Required fields
        if not data.get('name'):
            result.add_error('Company name is required')
        elif len(data['name'].strip()) < 2:
            result.add_error('Company name must be at least 2 characters')
        elif len(data['name']) > 255:
            result.add_error('Company name must be less than 255 characters')
        
        # CIK validation
        cik = data.get('cik')
        if cik:
            cik_str = str(cik).strip()
            if not self.patterns['cik'].match(cik_str):
                result.add_error('CIK must be exactly 10 digits')
            elif cik_str.startswith('0000000000'):
                result.add_warning('CIK appears to be all zeros')
        
        # Ticker validation
        ticker = data.get('ticker')
        if ticker:
            ticker_str = str(ticker).strip().upper()
            if not self.patterns['ticker'].match(ticker_str):
                result.add_warning('Ticker format may be invalid (should be 1-5 uppercase letters)')
        
        # Headquarters location validation
        location = data.get('headquarters_location')
        if location and len(location) > 255:
            result.add_error('Headquarters location must be less than 255 characters')
        
        return result
    
    def _validate_lobbying(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate lobbying report data."""
        result = ValidationResult()
        
        # Amount validation
        amount = data.get('amount_spent')
        if amount is None:
            result.add_error('Lobbying amount is required')
        else:
            try:
                amount_decimal = Decimal(str(amount))
                if amount_decimal < 0:
                    result.add_error('Lobbying amount cannot be negative')
                elif amount_decimal > Decimal('1000000000'):  # 1 billion
                    result.add_warning('Lobbying amount is unusually high')
            except (InvalidOperation, ValueError):
                result.add_error('Invalid lobbying amount format')
        
        # Year validation
        year = data.get('year')
        if not year:
            result.add_error('Lobbying year is required')
        else:
            try:
                year_int = int(year)
                current_year = datetime.now().year
                if not (2000 <= year_int <= current_year + 1):
                    result.add_error(f'Lobbying year must be between 2000 and {current_year + 1}')
            except (ValueError, TypeError):
                result.add_error('Invalid lobbying year format')
        
        # Quarter validation
        quarter = data.get('quarter')
        if quarter is not None:
            try:
                quarter_int = int(quarter)
                if quarter_int not in [1, 2, 3, 4]:
                    result.add_error('Quarter must be 1, 2, 3, or 4')
            except (ValueError, TypeError):
                result.add_error('Invalid quarter format')
        
        # Issues validation
        issues = data.get('specific_issues')
        if issues and len(issues) > 10000:
            result.add_warning('Specific issues text is very long')
        
        # URL validation
        report_url = data.get('report_url')
        if report_url and not self.patterns['url'].match(report_url):
            result.add_warning('Report URL format may be invalid')
        
        return result
    
    def _validate_political(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate political contribution data."""
        result = ValidationResult()
        
        # Amount validation
        amount = data.get('amount')
        if amount is None:
            result.add_error('Political contribution amount is required')
        else:
            try:
                amount_decimal = Decimal(str(amount))
                if amount_decimal <= 0:
                    result.add_error('Political contribution amount must be positive')
                elif amount_decimal > Decimal('100000'):  # 100k limit
                    result.add_warning('Political contribution amount exceeds typical limits')
            except (InvalidOperation, ValueError):
                result.add_error('Invalid political contribution amount format')
        
        # Date validation
        contribution_date = data.get('date')
        if not contribution_date:
            result.add_error('Contribution date is required')
        else:
            try:
                if isinstance(contribution_date, str):
                    date_obj = datetime.strptime(contribution_date, '%Y-%m-%d').date()
                else:
                    date_obj = contribution_date
                
                if date_obj > date.today():
                    result.add_error('Contribution date cannot be in the future')
                elif date_obj < date(2000, 1, 1):
                    result.add_warning('Contribution date is very old')
            except ValueError:
                result.add_error('Invalid contribution date format')
        
        # Recipient name validation
        recipient_name = data.get('recipient_name')
        if not recipient_name:
            result.add_error('Recipient name is required')
        elif len(recipient_name.strip()) < 2:
            result.add_error('Recipient name must be at least 2 characters')
        
        # Election cycle validation
        election_cycle = data.get('election_cycle')
        if election_cycle:
            try:
                cycle_int = int(election_cycle)
                if not (2000 <= cycle_int <= 2030):
                    result.add_warning('Election cycle year seems unusual')
            except (ValueError, TypeError):
                result.add_warning('Invalid election cycle format')
        
        # Party validation
        party = data.get('recipient_party')
        if party and party not in ['Republican', 'Democrat', 'Independent', 'Other']:
            result.add_warning(f'Unusual party designation: {party}')
        
        return result
    
    def _validate_charitable(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate charitable grant data."""
        result = ValidationResult()
        
        # Amount validation
        amount = data.get('amount')
        if amount is None:
            result.add_error('Charitable grant amount is required')
        else:
            try:
                amount_decimal = Decimal(str(amount))
                if amount_decimal <= 0:
                    result.add_error('Charitable grant amount must be positive')
                elif amount_decimal > Decimal('10000000'):  # 10 million
                    result.add_warning('Charitable grant amount is unusually high')
            except (InvalidOperation, ValueError):
                result.add_error('Invalid charitable grant amount format')
        
        # Fiscal year validation
        fiscal_year = data.get('fiscal_year')
        if not fiscal_year:
            result.add_error('Fiscal year is required')
        else:
            try:
                year_int = int(fiscal_year)
                current_year = datetime.now().year
                if not (2000 <= year_int <= current_year + 1):
                    result.add_error(f'Fiscal year must be between 2000 and {current_year + 1}')
            except (ValueError, TypeError):
                result.add_error('Invalid fiscal year format')
        
        # Recipient name validation
        recipient_name = data.get('recipient_name')
        if not recipient_name:
            result.add_error('Recipient name is required')
        elif len(recipient_name.strip()) < 2:
            result.add_error('Recipient name must be at least 2 characters')
        
        # EIN validation
        ein = data.get('recipient_ein')
        if ein and not self.patterns['ein'].match(str(ein).replace('-', '')):
            result.add_warning('EIN format may be invalid')
        
        # Category validation
        category = data.get('recipient_category')
        if category:
            valid_categories = [
                'Religious', 'Education', 'Healthcare', 'Environment',
                'Arts', 'Human Services', 'International', 'Other'
            ]
            if category not in valid_categories:
                result.add_warning(f'Unusual recipient category: {category}')
        
        # Description validation
        description = data.get('grant_description')
        if description and len(description) > 5000:
            result.add_warning('Grant description is very long')
        
        return result
    
    def _validate_financial(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate financial summary data."""
        result = ValidationResult()
        
        # Fiscal year validation
        fiscal_year = data.get('fiscal_year')
        if not fiscal_year:
            result.add_error('Fiscal year is required')
        else:
            try:
                year_int = int(fiscal_year)
                current_year = datetime.now().year
                if not (2000 <= year_int <= current_year + 1):
                    result.add_error(f'Fiscal year must be between 2000 and {current_year + 1}')
            except (ValueError, TypeError):
                result.add_error('Invalid fiscal year format')
        
        # Revenue validation
        revenue = data.get('total_revenue')
        if revenue is not None:
            try:
                revenue_decimal = Decimal(str(revenue))
                if revenue_decimal < 0:
                    result.add_error('Total revenue cannot be negative')
                elif revenue_decimal > Decimal('1000000000000'):  # 1 trillion
                    result.add_warning('Total revenue is unusually high')
            except (InvalidOperation, ValueError):
                result.add_error('Invalid total revenue format')
        
        # Net income validation
        net_income = data.get('net_income')
        if net_income is not None:
            try:
                income_decimal = Decimal(str(net_income))
                if income_decimal > Decimal('100000000000'):  # 100 billion
                    result.add_warning('Net income is unusually high')
            except (InvalidOperation, ValueError):
                result.add_error('Invalid net income format')
        
        # Revenue vs net income consistency
        if revenue is not None and net_income is not None:
            try:
                revenue_decimal = Decimal(str(revenue))
                income_decimal = Decimal(str(net_income))
                if revenue_decimal > 0 and abs(income_decimal) > revenue_decimal:
                    result.add_warning('Net income magnitude exceeds total revenue')
            except (InvalidOperation, ValueError):
                pass
        
        return result
    
    def validate_batch(self, data_type: str, data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate a batch of data records.
        
        Args:
            data_type: Type of data to validate
            data_list: List of data dictionaries to validate
            
        Returns:
            Dictionary with batch validation results
        """
        results = []
        valid_count = 0
        error_count = 0
        warning_count = 0
        
        for i, data in enumerate(data_list):
            result = self.validate_data(data_type, data)
            results.append({
                'index': i,
                'data': data,
                'result': result.to_dict()
            })
            
            if result.valid:
                valid_count += 1
            else:
                error_count += 1
            
            warning_count += len(result.warnings)
        
        return {
            'total_records': len(data_list),
            'valid_records': valid_count,
            'invalid_records': error_count,
            'total_warnings': warning_count,
            'validation_rate': valid_count / len(data_list) if data_list else 0,
            'results': results
        }


# Global validator instance
data_validator = DataValidator()


def validate_company_data(data: Dict[str, Any]) -> ValidationResult:
    """Convenience function to validate company data."""
    return data_validator.validate_data('company', data)


def validate_lobbying_data(data: Dict[str, Any]) -> ValidationResult:
    """Convenience function to validate lobbying data."""
    return data_validator.validate_data('lobbying', data)


def validate_political_data(data: Dict[str, Any]) -> ValidationResult:
    """Convenience function to validate political contribution data."""
    return data_validator.validate_data('political', data)


def validate_charitable_data(data: Dict[str, Any]) -> ValidationResult:
    """Convenience function to validate charitable grant data."""
    return data_validator.validate_data('charitable', data)


def validate_financial_data(data: Dict[str, Any]) -> ValidationResult:
    """Convenience function to validate financial data."""
    return data_validator.validate_data('financial', data)
