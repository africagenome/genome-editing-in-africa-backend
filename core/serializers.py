#core/serializers.py
from rest_framework import serializers
from .models import *


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'name', 'code', 'description', 'order']


class CountryListSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source='region.name', read_only=True)
    
    class Meta:
        model = Country
        fields = ['id', 'name', 'code', 'region', 'region_name', 'flag_emoji',
                  'biosafety_status', 'readiness_score', 'active_projects',
                  'confined_field_trials', 'publications_count']


class CountryDetailSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source='region.name', read_only=True)
    
    class Meta:
        model = Country
        fields = '__all__'


from rest_framework import serializers

class InstitutionSerializer(serializers.ModelSerializer):
    # Returns a list of country IDs for writes/reads
    countries = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Country.objects.all(),
        required=False
    )
    
    # Returns detailed array of country objects (read-only)
    countries_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Institution
        fields = [
            'id', 'name', 'acronym', 'type', 'countries', 'countries_details', 
            'website', 'email', 'phone', 'address', 'description', 
            'logo', 'established_year', 'is_active'
        ]

    def get_countries_details(self, obj):
        """Returns a list of dicts with name and code for all associated countries."""
        return [
            {
                'id': country.id,
                'name': country.name,
                'code': getattr(country, 'code', None) # Safely get code if it exists
            } 
            for country in obj.countries.all()
        ]


class ExpertListSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source='institution.name', read_only=True)
    country_name = serializers.CharField(source='country.name', read_only=True)
    country_code = serializers.CharField(source='country.code', read_only=True)
    
    class Meta:
        model = Expert
        fields = ['id', 'name', 'title', 'institution', 'institution_name',
                  'country', 'country_name', 'country_code', 'sector',
                  'expertise', 'is_verified', 'is_featured', 'profile_image']


class ExpertDetailSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source='institution.name', read_only=True)
    country_name = serializers.CharField(source='country.name', read_only=True)
    
    class Meta:
        model = Expert
        fields = '__all__'


# ============= ORGANISM SERIALIZERS =============

class OrganismCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Organism Category (Plant, Animal, Micro-organism, etc.)
    """
    organism_count = serializers.SerializerMethodField()
    category_type_display = serializers.CharField(source='get_category_type_display', read_only=True)
    
    class Meta:
        model = OrganismCategory
        fields = ['id', 'name', 'category_type', 'category_type_display', 'description', 
                  'icon', 'color_code', 'order', 'is_active', 'organism_count']
    
    def get_organism_count(self, obj):
        return obj.organisms.filter(is_active=True).count()


class OrganismListSerializer(serializers.ModelSerializer):
    """
    List serializer for Organism (lightweight)
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_type = serializers.CharField(source='category.category_type', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)
    category_color = serializers.CharField(source='category.color_code', read_only=True)
    display_name = serializers.SerializerMethodField()
    common_name_display = serializers.CharField(source='get_common_name_display', read_only=True)
    scientific_name_display = serializers.CharField(source='get_scientific_name_display', read_only=True)
    
    class Meta:
        model = Organism
        fields = ['id', 'common_name', 'common_name_display', 'scientific_name', 
                  'scientific_name_display', 'custom_name', 'display_name',
                  'category', 'category_name', 'category_type', 'category_icon', 
                  'category_color', 'icon', 'image', 'is_featured', 'is_active',
                  'genome_size_mb', 'chromosome_count']
    
    def get_display_name(self, obj):
        return obj.display_name


class OrganismDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Organism
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_type = serializers.CharField(source='category.category_type', read_only=True)
    category_type_display = serializers.CharField(source='category.get_category_type_display', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)
    category_color = serializers.CharField(source='category.color_code', read_only=True)
    common_name_display = serializers.CharField(source='get_common_name_display', read_only=True)
    scientific_name_display = serializers.CharField(source='get_scientific_name_display', read_only=True)
    display_name = serializers.SerializerMethodField()
    projects_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Organism
        fields = '__all__'
    
    def get_display_name(self, obj):
        return obj.display_name
    
    def get_projects_count(self, obj):
        return obj.projects.count()


# ============= PROJECT SERIALIZERS (UPDATED) =============

class ProjectListSerializer(serializers.ModelSerializer):
    """
    List serializer for Project (lightweight)
    """
    country_name = serializers.CharField(source='country.name', read_only=True)
    lead_institution_name = serializers.CharField(source='lead_institution.name', read_only=True)
    primary_organism_name = serializers.SerializerMethodField()
    primary_organism_display = serializers.SerializerMethodField()
    organisms_list = serializers.SerializerMethodField()
    organisms_count = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    technology_display = serializers.CharField(source='get_technology_display', read_only=True)
    sector_display = serializers.CharField(source='get_sector_display', read_only=True)
    
    class Meta:
        model = Project
        fields = ['id', 'title', 'slug', 'country', 'country_name', 'sector', 'sector_display',
                  'primary_organism', 'primary_organism_name', 'primary_organism_display',
                  'organisms', 'organisms_list', 'organisms_count',
                  'technology', 'technology_display', 'status', 'status_display',
                  'lead_institution', 'lead_institution_name', 'start_year', 'end_year',
                  'funding_amount', 'funding_source', 'cft_location', 'created_at']
    
    def get_primary_organism_name(self, obj):
        if obj.primary_organism:
            return obj.primary_organism.common_name
        return None
    
    def get_primary_organism_display(self, obj):
        if obj.primary_organism:
            return str(obj.primary_organism)
        return None
    
    def get_organisms_list(self, obj):
        return [{'id': org.id, 'name': str(org), 'common_name': org.common_name} 
                for org in obj.organisms.all()]
    
    def get_organisms_count(self, obj):
        return obj.organisms.count()


class ProjectDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Project
    """
    country_name = serializers.CharField(source='country.name', read_only=True)
    country_code = serializers.CharField(source='country.code', read_only=True)
    lead_institution_name = serializers.CharField(source='lead_institution.name', read_only=True)
    lead_institution_detail = InstitutionSerializer(source='lead_institution', read_only=True)
    partners_list = InstitutionSerializer(many=True, read_only=True, source='partners')
    
    # Organism relationships
    primary_organism_detail = OrganismListSerializer(source='primary_organism', read_only=True)
    organisms_detail = OrganismListSerializer(source='organisms', many=True, read_only=True)
    organisms_by_category = serializers.SerializerMethodField()
    
    # Display fields
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    technology_display = serializers.CharField(source='get_technology_display', read_only=True)
    sector_display = serializers.CharField(source='get_sector_display', read_only=True)
    
    class Meta:
        model = Project
        fields = '__all__'
    
    def get_organisms_by_category(self, obj):
        """Group organisms by category"""
        from collections import defaultdict
        categories = defaultdict(list)
        for organism in obj.organisms.all():
            category_name = organism.category.name
            categories[category_name].append({
                'id': organism.id,
                'name': str(organism),
                'common_name': organism.common_name,
                'scientific_name': organism.scientific_name,
                'category': organism.category.id,
                'category_name': category_name,
                'category_type': organism.category.category_type,
                'category_icon': organism.category.icon,
                'category_color': organism.category.color_code,
            })
        return dict(categories)


class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating Projects
    """
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


# ============= PUBLICATION SERIALIZERS =============

class PublicationListSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    topic_display = serializers.CharField(source='get_topic_display', read_only=True)
    
    class Meta:
        model = Publication
        fields = ['id', 'title', 'authors', 'year', 'type', 'type_display', 'topic', 
                  'topic_display', 'country', 'country_name', 'doi', 'downloads', 
                  'is_featured', 'is_open_access']


class PublicationDetailSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)
    region_name = serializers.CharField(source='region.name', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    topic_display = serializers.CharField(source='get_topic_display', read_only=True)
    language_display = serializers.CharField(source='get_language_display', read_only=True)
    
    class Meta:
        model = Publication
        fields = '__all__'


# ============= PROTOCOL SERIALIZERS =============

class ProtocolListSerializer(serializers.ModelSerializer):
    author_institution_name = serializers.CharField(source='author_institution.name', read_only=True)
    technology_display = serializers.CharField(source='get_technology_display', read_only=True)
    protocol_type_display = serializers.CharField(source='get_protocol_type_display', read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    
    class Meta:
        model = Protocol
        fields = ['id', 'title', 'technology', 'technology_display', 'crop_application',
                  'protocol_type', 'protocol_type_display', 'difficulty', 'difficulty_display',
                  'author_institution', 'author_institution_name', 'downloads', 
                  'rating', 'rating_count', 'is_featured']


class ProtocolDetailSerializer(serializers.ModelSerializer):
    author_institution_name = serializers.CharField(source='author_institution.name', read_only=True)
    technology_display = serializers.CharField(source='get_technology_display', read_only=True)
    protocol_type_display = serializers.CharField(source='get_protocol_type_display', read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    
    class Meta:
        model = Protocol
        fields = '__all__'


# ============= CONSULTATION SERIALIZERS =============

class ConsultationSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)
    region_name = serializers.CharField(source='region.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    days_remaining = serializers.SerializerMethodField()
    is_open = serializers.SerializerMethodField()
    
    class Meta:
        model = Consultation
        fields = ['id', 'title', 'slug', 'description', 'country', 'country_name',
                  'region', 'region_name', 'document', 'external_link', 
                  'opening_date', 'closing_date', 'status', 'status_display',
                  'contact_email', 'instructions', 'days_remaining', 'is_open']
    
    def get_days_remaining(self, obj):
        from django.utils import timezone
        if obj.status == 'open' and obj.closing_date:
            days = (obj.closing_date - timezone.now().date()).days
            return max(0, days)
        return 0
    
    def get_is_open(self, obj):
        from django.utils import timezone
        return obj.status == 'open' and obj.closing_date >= timezone.now().date()


class ConsultationSubmissionSerializer(serializers.ModelSerializer):
    stakeholder_type_display = serializers.CharField(source='get_stakeholder_type_display', read_only=True)
    
    class Meta:
        model = ConsultationSubmission
        fields = ['id', 'consultation', 'name', 'email', 'organization',
                  'stakeholder_type', 'stakeholder_type_display', 'country',
                  'comments', 'attachments', 'is_public', 'is_approved', 'submitted_at']
        read_only_fields = ['submitted_at', 'is_approved']


# ============= NEWS SERIALIZERS =============

class NewsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ['id', 'title', 'slug', 'summary', 'featured_image',
                  'published_date', 'is_featured', 'views']


class NewsDetailSerializer(serializers.ModelSerializer):
    countries_list = CountryListSerializer(many=True, read_only=True, source='countries')
    
    class Meta:
        model = News
        fields = '__all__'


# ============= FAQ SERIALIZER =============

class FAQSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'category', 'category_display', 'order']


# ============= GLOSSARY SERIALIZER =============

class GlossaryTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlossaryTerm
        fields = ['id', 'term', 'definition', 'abbreviation', 'category', 'related_terms']


# ============= FUNDING OPPORTUNITY SERIALIZER =============

class FundingOpportunitySerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    days_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = FundingOpportunity
        fields = '__all__'
    
    def get_days_remaining(self, obj):
        from django.utils import timezone
        if obj.status in ['open', 'closing_soon'] and obj.deadline:
            days = (obj.deadline - timezone.now().date()).days
            return max(0, days)
        return 0


# ============= EVENT SERIALIZERS =============

class EventListSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    
    class Meta:
        model = Event
        fields = ['id', 'title', 'slug', 'event_type', 'event_type_display', 
                  'start_date', 'end_date', 'venue', 'country', 'country_name', 
                  'is_virtual', 'is_featured']


class EventDetailSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)
    region_name = serializers.CharField(source='country.region.name', read_only=True)
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    
    class Meta:
        model = Event
        fields = '__all__'


# ============= DASHBOARD STATS SERIALIZER =============

class DashboardStatsSerializer(serializers.Serializer):
    """
    Serializer for dashboard statistics
    """
    total_countries = serializers.IntegerField()
    total_projects = serializers.IntegerField()
    total_publications = serializers.IntegerField()
    total_experts = serializers.IntegerField()
    total_protocols = serializers.IntegerField()
    total_organisms = serializers.IntegerField()
    projects_by_status = serializers.DictField()
    projects_by_technology = serializers.DictField()
    projects_by_sector = serializers.DictField()
    publications_by_year = serializers.DictField()
    countries_by_readiness = serializers.DictField()
    organisms_by_category = serializers.DictField()



class MultilateralAgreementSerializer(serializers.ModelSerializer):
    agreement_type_display = serializers.CharField(source='get_agreement_type_display', read_only=True)
    
    class Meta:
        model = MultilateralAgreement
        fields = [
            'id', 'agreement_type', 'agreement_type_display', 'name',
            'signed_date', 'ratified_date', 'accession_date',
            'reference_url', 'notes', 'is_active'
        ]


class RegulatoryInstitutionSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    institution_name = serializers.CharField(source='institution.name', read_only=True)
    institution_detail = InstitutionSerializer(source='institution', read_only=True)
    
    class Meta:
        model = RegulatoryInstitution
        fields = [
            'id', 'institution', 'institution_name', 'institution_detail',
            'role', 'role_display', 'mandate', 'website',
            'contact_email', 'contact_phone', 'order', 'is_active'
        ]


class RegulatoryInstrumentSerializer(serializers.ModelSerializer):
    instrument_type_display = serializers.CharField(source='get_instrument_type_display', read_only=True)
    coverage_display = serializers.CharField(source='get_coverage_display', read_only=True)
    
    class Meta:
        model = RegulatoryInstrument
        fields = [
            'id', 'title', 'instrument_type', 'instrument_type_display',
            'date_enacted', 'date_amended', 'coverage', 'coverage_display',
            'summary', 'reference_url', 'document_file', 'is_current', 'order'
        ]


class GedRegulatoryStatusSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = GedRegulatoryStatus
        fields = [
            'id', 'category', 'category_display', 'status', 'status_display',
            'description', 'notes', 'last_updated'
        ]


class RegulatoryTimelineSerializer(serializers.ModelSerializer):
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    
    class Meta:
        model = RegulatoryTimeline
        fields = [
            'id', 'event_type', 'event_type_display', 'title',
            'description', 'event_date', 'reference', 'order'
        ]


class RegulatoryFrameworkListSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)
    country_code = serializers.CharField(source='country.code', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    approach_display = serializers.CharField(source='get_approach_display', read_only=True)
    
    class Meta:
        model = RegulatoryFramework
        fields = [
            'id', 'country', 'country_name', 'country_code',
            'status', 'status_display', 'approach', 'approach_display',
            'summary', 'biosafety_act_date', 'ged_guidelines_date',
            'last_updated'
        ]


class RegulatoryFrameworkDetailSerializer(serializers.ModelSerializer):
    country_detail = CountryListSerializer(source='country', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    approach_display = serializers.CharField(source='get_approach_display', read_only=True)
    
    # Nested serializers
    multilateral_agreements = MultilateralAgreementSerializer(many=True, read_only=True)
    regulatory_institutions = RegulatoryInstitutionSerializer(many=True, read_only=True)
    regulatory_instruments = RegulatoryInstrumentSerializer(many=True, read_only=True)
    ged_regulatory_statuses = GedRegulatoryStatusSerializer(many=True, read_only=True)
    regulatory_timeline = RegulatoryTimelineSerializer(many=True, read_only=True)
    
    class Meta:
        model = RegulatoryFramework
        fields = [
            'id', 'country', 'country_detail', 'status', 'status_display',
            'approach', 'approach_display', 'summary', 'last_updated',
            'biosafety_act_date', 'biosafety_regulations_date', 'ged_guidelines_date',
            'created_at', 'updated_at',
            'multilateral_agreements', 'regulatory_institutions',
            'regulatory_instruments', 'ged_regulatory_statuses',
            'regulatory_timeline'
        ]


class RegulatoryFrameworkCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegulatoryFramework
        fields = [
            'country', 'status', 'approach', 'summary',
            'biosafety_act_date', 'biosafety_regulations_date', 'ged_guidelines_date'
        ]



#Kiambe
class InfrastructureCategorySerializer(serializers.ModelSerializer):
    category_type_display = serializers.CharField(source='get_category_type_display', read_only=True)
    facility_count = serializers.SerializerMethodField()
    
    class Meta:
        model = InfrastructureCategory
        fields = [
            'id', 'name', 'category_type', 'category_type_display',
            'description', 'icon', 'order', 'is_active', 'facility_count'
        ]
    
    def get_facility_count(self, obj):
        return obj.laboratory_facilities.filter(is_active=True).count()


class EquipmentSerializer(serializers.ModelSerializer):
    equipment_type_display = serializers.CharField(source='get_equipment_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    condition_display = serializers.CharField(source='get_condition_display', read_only=True)
    
    class Meta:
        model = Equipment
        fields = [
            'id', 'name', 'equipment_type', 'equipment_type_display', 'model',
            'manufacturer', 'serial_number', 'facility', 'status', 'status_display',
            'condition', 'condition_display', 'specifications', 'acquisition_date',
            'last_maintenance_date', 'next_maintenance_date', 'is_shared',
            'operational_hours', 'contact_person', 'is_active'
        ]


class LaboratoryFacilityListSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source='institution.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    biosafety_level_display = serializers.CharField(source='get_biosafety_level_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    equipment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = LaboratoryFacility
        fields = [
            'id', 'institution', 'institution_name', 'category', 'category_name',
            'name', 'facility_type', 'biosafety_level', 'biosafety_level_display',
            'status', 'status_display', 'description', 'equipment_count',
            'researcher_count', 'is_active'
        ]
    
    def get_equipment_count(self, obj):
        return obj.equipment.filter(is_active=True).count()


class LaboratoryFacilityDetailSerializer(serializers.ModelSerializer):
    institution_detail = InstitutionSerializer(source='institution', read_only=True)
    category_detail = InfrastructureCategorySerializer(source='category', read_only=True)
    biosafety_level_display = serializers.CharField(source='get_biosafety_level_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    equipment = EquipmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = LaboratoryFacility
        fields = [
            'id', 'institution', 'institution_detail', 'category', 'category_detail',
            'name', 'facility_type', 'biosafety_level', 'biosafety_level_display',
            'status', 'status_display', 'description', 'limitations', 'support_needed',
            'equipment_list', 'equipment_needs', 'capacity_description',
            'researcher_count', 'contact_person', 'contact_email', 'contact_phone',
            'established_year', 'last_updated', 'is_active', 'equipment',
            'created_at', 'updated_at'
        ]


class LaboratoryFacilityCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LaboratoryFacility
        fields = [
            'institution', 'category', 'name', 'facility_type', 'biosafety_level',
            'status', 'description', 'limitations', 'support_needed',
            'equipment_list', 'equipment_needs', 'capacity_description',
            'researcher_count', 'contact_person', 'contact_email', 'contact_phone',
            'established_year', 'is_active'
        ]


class InfrastructureProjectSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)
    institution_name = serializers.CharField(source='institution.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = InfrastructureProject
        fields = [
            'id', 'title', 'slug', 'country', 'country_name', 'institution',
            'institution_name', 'description', 'objectives', 'expected_outcomes',
            'status', 'status_display', 'priority', 'priority_display',
            'start_date', 'end_date', 'funding_amount', 'funding_source',
            'partners', 'equipment_needed', 'contact_person', 'contact_email',
            'is_active', 'created_at', 'updated_at'
        ]


class TrainingCapacitySerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source='institution.name', read_only=True)
    training_type_display = serializers.CharField(source='get_training_type_display', read_only=True)
    skill_level_display = serializers.CharField(source='get_skill_level_display', read_only=True)
    
    class Meta:
        model = TrainingCapacity
        fields = [
            'id', 'institution', 'institution_name', 'title', 'training_type',
            'training_type_display', 'description', 'skill_level',
            'skill_level_display', 'max_participants', 'current_enrollment',
            'topics_covered', 'equipment_used', 'start_date', 'end_date',
            'duration', 'contact_person', 'contact_email', 'is_active',
            'is_featured', 'created_at', 'updated_at'
        ]


class InfrastructureAssessmentSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)
    assessment_area_display = serializers.CharField(source='get_assessment_area_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = InfrastructureAssessment
        fields = [
            'id', 'country', 'country_name', 'assessment_date',
            'assessment_area', 'assessment_area_display', 'title',
            'description', 'current_status', 'challenges', 'recommendations',
            'priority', 'priority_display', 'score', 'created_at', 'updated_at'
        ]