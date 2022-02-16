from kas.models import PensionCompany, Person, PersonTaxYear, PolicyDocument, PolicyTaxYear, TaxYear
from rest_framework import serializers


class PensionCompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = PensionCompany
        fields = ['id', 'name', 'address', 'email', 'phone', 'res', 'agreement_present']
        read_only_fields = ['id']


class TaxYearSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaxYear
        fields = ['id', 'year', 'days_in_year', 'year_part']
        read_only_fields = ['id', 'year', 'days_in_year', 'year_part']


class PersonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Person
        fields = ['id', 'cpr']
        read_only_fields = ['id']


class PersonTaxYearSerializer(serializers.ModelSerializer):

    class Meta:
        model = PersonTaxYear
        fields = [
            'id', 'tax_year', 'person', 'fully_tax_liable', 'number_of_days', 'days_in_year_factor',
            'foreign_pension_notes', 'general_notes', 'updated_by',
        ]
        read_only_fields = ['id', 'fully_tax_liable', 'number_of_days', 'days_in_year_factor']

    person = serializers.SlugRelatedField(queryset=Person.objects.all(), slug_field='cpr')
    tax_year = serializers.SlugRelatedField(queryset=TaxYear.objects.all(), slug_field='year')


class PolicyDocumentSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        validated_data['person_tax_year_id'] = validated_data['policy_tax_year'].person_tax_year_id
        return super(PolicyDocumentSerializer, self).create(validated_data)

    class Meta:
        model = PolicyDocument
        fields = ['id', 'policy_tax_year', 'name', 'description', 'file']
        read_only_fields = ['id']

    policy_tax_year = serializers.PrimaryKeyRelatedField(queryset=PolicyTaxYear.objects.all())


class PolicyTaxYearSerializer(serializers.ModelSerializer):

    class Meta:
        model = PolicyTaxYear
        fields = [
            'id', 'policy_number', 'prefilled_amount', 'self_reported_amount', 'pension_company',
            'person_tax_year', 'preliminary_paid_amount', 'from_pension', 'calculated_result',
            'foreign_paid_amount_self_reported', 'foreign_paid_amount_actual', 'applied_deduction_from_previous_years',
            'available_deduction_from_previous_years', 'year_adjusted_amount', 'documents', 'active',
            'updated_by',
        ]
        read_only_fields = [
            'id', 'pension_company', 'person_tax_year', 'documents', 'active', 'prefilled_amount',
            'applied_deduction_from_previous_years', 'available_deduction_from_previous_years',
        ]
        depth = 2

    # Explicitly define this to be required; PolicyTaxYears may have this empty in the DB, but we don't accept incoming objects without it
    self_reported_amount = serializers.IntegerField(required=True)

    person_tax_year = serializers.PrimaryKeyRelatedField(queryset=PersonTaxYear.objects.all())
    pension_company = serializers.PrimaryKeyRelatedField(queryset=PensionCompany.objects.all())
    # Serializer based on the prefetch defined in the viewset. "documents" must match the prefetch to_attr
    documents = PolicyDocumentSerializer(many=True, required=False, allow_null=True)

    def get_citizen_documents(self, policy_tax_year):
        return PolicyDocumentSerializer(
            instance=policy_tax_year.policy_documents.filter(uploaded_by__isnull=True),
            many=True,
            context=self.context
        ).data

    def create(self, validated_data):
        if validated_data.get('self_reported_amount') is not None:
            validated_data['active_amount'] = PolicyTaxYear.ACTIVE_AMOUNT_SELF_REPORTED
        instance = super(PolicyTaxYearSerializer, self).create(validated_data)
        instance.recalculate()
        instance.save()
        return instance

    def update(self, instance, validated_data):
        if validated_data.get('self_reported_amount') is not None:
            validated_data['active_amount'] = PolicyTaxYear.ACTIVE_AMOUNT_SELF_REPORTED
        instance = super(PolicyTaxYearSerializer, self).update(instance, validated_data)
        instance.recalculate()
        instance.save()
        return instance
