from django.contrib import admin
from .models import Company, FinancialSummary, LobbyingReport, PoliticalContribution, CharitableGrant


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'ticker', 'cik', 'headquarters_location', 'created_at']
    search_fields = ['name', 'ticker', 'cik']
    list_filter = ['created_at']
    ordering = ['name']


@admin.register(FinancialSummary)
class FinancialSummaryAdmin(admin.ModelAdmin):
    list_display = ['company', 'fiscal_year', 'total_revenue', 'net_income']
    list_filter = ['fiscal_year', 'company']
    search_fields = ['company__name']
    ordering = ['company', '-fiscal_year']


@admin.register(LobbyingReport)
class LobbyingReportAdmin(admin.ModelAdmin):
    list_display = ['company', 'year', 'quarter', 'amount_spent']
    list_filter = ['year', 'quarter', 'company']
    search_fields = ['company__name', 'specific_issues']
    ordering = ['company', '-year', '-quarter']


@admin.register(PoliticalContribution)
class PoliticalContributionAdmin(admin.ModelAdmin):
    list_display = ['company_pac_id', 'recipient_name', 'recipient_party', 'amount', 'election_cycle', 'date']
    list_filter = ['recipient_party', 'election_cycle', 'date']
    search_fields = ['company_pac_id', 'recipient_name']
    ordering = ['-date']


@admin.register(CharitableGrant)
class CharitableGrantAdmin(admin.ModelAdmin):
    list_display = ['company', 'recipient_name', 'amount', 'fiscal_year', 'recipient_category']
    list_filter = ['fiscal_year', 'recipient_category', 'company']
    search_fields = ['company__name', 'recipient_name', 'grant_description']
    ordering = ['company', '-fiscal_year']
