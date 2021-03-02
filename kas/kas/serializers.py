from kas.models import PensionCompany, Person, PersonTaxYear, PolicyDocument, PolicyTaxYear, TaxYear
from rest_framework import serializers


class PensionCompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = PensionCompany
        fields = ['id', 'name', 'address', 'email', 'phone', 'cvr']
        read_only_fields = ['id']


class TaxYearSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaxYear
        fields = ['id', 'year']
        read_only_fields = ['id']


class PersonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Person
        fields = ['id', 'cpr']
        read_only_fields = ['id']


class PersonTaxYearSerializer(serializers.ModelSerializer):

    class Meta:
        model = PersonTaxYear
        fields = ['id', 'tax_year', 'person', 'fully_tax_liable']
        read_only_fields = ['id', 'fully_tax_liable']

    person = serializers.SlugRelatedField(queryset=Person.objects.all(), slug_field='cpr')
    tax_year = serializers.SlugRelatedField(queryset=TaxYear.objects.all(), slug_field='year')


class PolicyTaxYearSerializer(serializers.ModelSerializer):

    class Meta:
        model = PolicyTaxYear
        fields = ['id', 'policy_number', 'prefilled_amount', 'self_reported_amount', 'pension_company', 'person_tax_year', 'preliminary_paid_amount', 'from_pension']
        read_only_fields = ['id', 'policy_number', 'pension_company', 'person_tax_year']
        depth = 2

    person_tax_year = serializers.PrimaryKeyRelatedField(queryset=PersonTaxYear.objects.all())
    pension_company = serializers.SlugRelatedField(queryset=PensionCompany.objects.all(), slug_field='cvr')


class PolicyDocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = PolicyDocument
        fields = ['id', 'policy_tax_year', 'name', 'description', 'file']
        read_only_fields = ['id']

    policy_tax_year = serializers.PrimaryKeyRelatedField(queryset=PolicyTaxYear.objects.all())
