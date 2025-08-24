from django.db import models


class Company(models.Model):
    """Central table for company information."""
    name = models.CharField(max_length=255)
    ticker = models.CharField(max_length=10, blank=True, null=True)
    cik = models.CharField(max_length=20, blank=True, null=True)  # SEC Central Index Key
    headquarters_location = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Companies"
        db_table = 'companies'

    def __str__(self):
        return self.name


class FinancialSummary(models.Model):
    """Stores contextual financial data."""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='financial_summaries')
    fiscal_year = models.IntegerField()
    total_revenue = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    net_income = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Financial Summaries"
        db_table = 'financial_summaries'
        unique_together = ['company', 'fiscal_year']

    def __str__(self):
        return f"{self.company.name} - {self.fiscal_year}"


class LobbyingReport(models.Model):
    """Stores lobbying data from Senate filings."""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='lobbying_reports')
    year = models.IntegerField()
    quarter = models.IntegerField()
    amount_spent = models.DecimalField(max_digits=15, decimal_places=2)
    specific_issues = models.TextField(blank=True, null=True)
    report_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Lobbying Reports"
        db_table = 'lobbying_reports'
        unique_together = ['company', 'year', 'quarter']

    def __str__(self):
        return f"{self.company.name} - Q{self.quarter} {self.year}"


class PoliticalContribution(models.Model):
    """Stores campaign contribution data from the FEC."""
    company_pac_id = models.CharField(max_length=255)  # PAC name or identifier
    recipient_name = models.CharField(max_length=255)
    recipient_party = models.CharField(max_length=50, blank=True, null=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateField()
    election_cycle = models.CharField(max_length=10)  # e.g., "2024", "2022"
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Political Contributions"
        db_table = 'political_contributions'

    def __str__(self):
        return f"{self.company_pac_id} -> {self.recipient_name} ({self.election_cycle})"


class CharitableGrant(models.Model):
    """Stores grant data from IRS Form 990-PF."""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='charitable_grants')
    recipient_name = models.CharField(max_length=255)
    recipient_ein = models.CharField(max_length=20, blank=True, null=True)  # EIN of the nonprofit
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    fiscal_year = models.IntegerField()
    grant_description = models.TextField(blank=True, null=True)
    recipient_category = models.CharField(max_length=100, blank=True, null=True)  # e.g., "Religious," "Education," "Healthcare"
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Charitable Grants"
        db_table = 'charitable_grants'

    def __str__(self):
        return f"{self.company.name} -> {self.recipient_name} ({self.fiscal_year})"
