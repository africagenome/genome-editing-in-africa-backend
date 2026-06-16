from rest_framework import serializers
from .models import (
    Region, Country, Institution, Expert, Project, Publication,
    Protocol, Consultation, ConsultationSubmission, News, FAQ,
    GlossaryTerm, FundingOpportunity, Event, OrganismCategory, Organism
)


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


class InstitutionSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)
    country_code = serializers.CharField(source='country.code', read_only=True)
    
    class Meta:
        model = Institution
        fields = ['id', 'name', 'acronym', 'type', 'country', 'country_name',
                  'country_code', 'website', 'email', 'phone', 'address',
                  'description', 'logo', 'established_year', 'is_active']


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