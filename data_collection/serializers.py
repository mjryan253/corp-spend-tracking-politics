from rest_framework import serializers
from .models import Company, FinancialSummary, LobbyingReport, PoliticalContribution, CharitableGrant


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class FinancialSummarySerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = FinancialSummary
        fields = '__all__'


class LobbyingReportSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = LobbyingReport
        fields = '__all__'


class PoliticalContributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoliticalContribution
        fields = '__all__'


class CharitableGrantSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = CharitableGrant
        fields = '__all__'


class CompanyDetailSerializer(serializers.ModelSerializer):
    financial_summaries = FinancialSummarySerializer(many=True, read_only=True)
    lobbying_reports = LobbyingReportSerializer(many=True, read_only=True)
    charitable_grants = CharitableGrantSerializer(many=True, read_only=True)
    
    class Meta:
        model = Company
        fields = '__all__'
