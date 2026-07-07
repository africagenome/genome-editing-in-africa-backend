# core/filters.py

from django_filters import rest_framework as filters
from django.db import models
from .models import *
from django_filters import FilterSet, CharFilter, NumberFilter, ChoiceFilter, BooleanFilter

class CountryFilter(filters.FilterSet):
    min_readiness = filters.NumberFilter(field_name='readiness_score', lookup_expr='gte')
    max_readiness = filters.NumberFilter(field_name='readiness_score', lookup_expr='lte')
    region = filters.NumberFilter(field_name='region__id')
    region_code = filters.CharFilter(field_name='region__code', lookup_expr='iexact')
    biosafety_status = filters.MultipleChoiceFilter(choices=Country.BIOSAFETY_STATUS)
    search = filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Country
        fields = ['region', 'biosafety_status', 'classification_approach', 'min_readiness', 'max_readiness']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(name__icontains=value) |
            models.Q(code__icontains=value)
        )


class InstitutionFilter(filters.FilterSet):
    countries = filters.NumberFilter(field_name='countries', lookup_expr='id')
    country_name = filters.CharFilter(field_name='countries__name', lookup_expr='icontains')
    type = filters.CharFilter(field_name='type', lookup_expr='icontains')
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    is_active = filters.BooleanFilter(field_name='is_active')
    search = filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Institution
        fields = {
            'type': ['exact'],
            'name': ['icontains', 'exact'],
            'is_active': ['exact'],
            'countries': ['exact', 'in'],
        }
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(name__icontains=value) |
            models.Q(acronym__icontains=value) |
            models.Q(description__icontains=value)
        )


class ProjectFilter(filters.FilterSet):
    min_year = filters.NumberFilter(field_name='start_year', lookup_expr='gte')
    max_year = filters.NumberFilter(field_name='start_year', lookup_expr='lte')
    country = filters.NumberFilter(field_name='country__id')
    country_code = filters.CharFilter(field_name='country__code', lookup_expr='iexact')
    region = filters.NumberFilter(field_name='country__region__id')
    technology = filters.MultipleChoiceFilter(choices=Project.TECH_CHOICES)
    status = filters.MultipleChoiceFilter(choices=Project.STATUS_CHOICES)
    sector = filters.MultipleChoiceFilter(choices=Project.SECTOR_CHOICES)
    search = filters.CharFilter(field_name='title', lookup_expr='icontains')
    
    class Meta:
        model = Project
        fields = ['status', 'technology', 'sector', 'country', 'region', 'min_year', 'max_year']


class ExpertFilter(filters.FilterSet):
    country = filters.NumberFilter(field_name='country__id')
    country_code = filters.CharFilter(field_name='country__code', lookup_expr='iexact')
    region = filters.NumberFilter(field_name='country__region__id')
    sector = filters.MultipleChoiceFilter(choices=Expert.SECTOR_CHOICES)
    expertise = filters.CharFilter(method='filter_expertise')
    is_verified = filters.BooleanFilter()
    is_featured = filters.BooleanFilter()
    search = filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Expert
        fields = ['sector', 'country', 'region', 'is_verified', 'is_featured']
    
    def filter_expertise(self, queryset, name, value):
        return queryset.filter(expertise__contains=[value])
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(name__icontains=value) |
            models.Q(institution__name__icontains=value) |
            models.Q(bio__icontains=value)
        )


class PublicationFilter(filters.FilterSet):
    min_year = filters.NumberFilter(field_name='year', lookup_expr='gte')
    max_year = filters.NumberFilter(field_name='year', lookup_expr='lte')
    country = filters.NumberFilter(field_name='country__id')
    region = filters.NumberFilter(field_name='region__id')
    type = filters.MultipleChoiceFilter(choices=Publication.TYPE_CHOICES)
    topic = filters.MultipleChoiceFilter(choices=Publication.TOPIC_CHOICES)
    language = filters.ChoiceFilter(choices=Publication.LANGUAGE_CHOICES)
    is_featured = filters.BooleanFilter()
    search = filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Publication
        fields = ['type', 'topic', 'year', 'country', 'region', 'language', 'is_featured']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(title__icontains=value) |
            models.Q(authors__icontains=value) |
            models.Q(abstract__icontains=value) |
            models.Q(keywords__icontains=value)
        )


class ProtocolFilter(filters.FilterSet):
    technology = filters.MultipleChoiceFilter(choices=Protocol.TECH_CHOICES)
    protocol_type = filters.MultipleChoiceFilter(choices=Protocol.TYPE_CHOICES)
    difficulty = filters.ChoiceFilter(choices=Protocol.DIFFICULTY_CHOICES)
    is_featured = filters.BooleanFilter()
    min_rating = filters.NumberFilter(field_name='rating', lookup_expr='gte')
    search = filters.CharFilter(field_name='title', lookup_expr='icontains')
    
    class Meta:
        model = Protocol
        fields = ['technology', 'protocol_type', 'difficulty', 'is_featured', 'min_rating']


class EventFilter(filters.FilterSet):
    event_type = filters.MultipleChoiceFilter(choices=Event.TYPE_CHOICES)
    country = filters.NumberFilter(field_name='country__id')
    start_date_from = filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_to = filters.DateFilter(field_name='start_date', lookup_expr='lte')
    is_virtual = filters.BooleanFilter()
    is_featured = filters.BooleanFilter()
    
    class Meta:
        model = Event
        fields = ['event_type', 'country', 'is_virtual', 'is_featured']


class OrganismFilter(filters.FilterSet):
    category = filters.NumberFilter(field_name='category__id')
    category_type = filters.CharFilter(field_name='category__category_type')
    search = filters.CharFilter(method='filter_search')
    min_genome_size = filters.NumberFilter(field_name='genome_size_mb', lookup_expr='gte')
    max_genome_size = filters.NumberFilter(field_name='genome_size_mb', lookup_expr='lte')
    
    class Meta:
        model = Organism
        fields = ['category', 'is_featured', 'is_active']
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(common_name__icontains=value) |
            models.Q(scientific_name__icontains=value) |
            models.Q(custom_name__icontains=value) |
            models.Q(description__icontains=value)
        )


class LaboratoryFacilityFilter(filters.FilterSet):
    """
    Filter for LaboratoryFacility model.
    Supports filtering by biosafety levels (MultiSelectField), status, category, institution, and country.
    """
    biosafety_level = filters.MultipleChoiceFilter(
        choices=LaboratoryFacility.BIOSAFETY_LEVELS,
        field_name='biosafety_level',
        lookup_expr='icontains'
    )
    biosafety_level_exact = filters.MultipleChoiceFilter(
        choices=LaboratoryFacility.BIOSAFETY_LEVELS,
        field_name='biosafety_level',
        lookup_expr='exact'
    )
    status = filters.MultipleChoiceFilter(
        choices=LaboratoryFacility.STATUS_CHOICES
    )
    category = filters.NumberFilter(field_name='category__id')
    category_name = filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    institution = filters.NumberFilter(field_name='institution__id')
    institution_name = filters.CharFilter(field_name='institution__name', lookup_expr='icontains')
    # Country filters - now direct field
    country = filters.NumberFilter(field_name='country__id')
    country_code = filters.CharFilter(field_name='country__code', lookup_expr='iexact')
    country_name = filters.CharFilter(field_name='country__name', lookup_expr='icontains')

    is_active = filters.BooleanFilter()
    min_researchers = filters.NumberFilter(field_name='researcher_count', lookup_expr='gte')
    max_researchers = filters.NumberFilter(field_name='researcher_count', lookup_expr='lte')
    search = filters.CharFilter(method='filter_search')
    
    class Meta:
        model = LaboratoryFacility
        fields = {
            'status': ['exact'],
            'biosafety_level': ['icontains', 'exact'],
            'category': ['exact'],
            'institution': ['exact'],
            'country': ['exact'], 
            'is_active': ['exact'],
            'researcher_count': ['gte', 'lte'],
        }
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(name__icontains=value) |
            models.Q(abbreviation__icontains=value) |
            models.Q(institution__name__icontains=value) |
            models.Q(country__name__icontains=value) | 
            models.Q(description__icontains=value) |
            models.Q(facility_type__icontains=value) |
            models.Q(equipment_list__icontains=value) |
            models.Q(support_needed__icontains=value)
        )




class NationalPriorityCropFilter(FilterSet):
    """
    Simplified filter set for NationalPriorityCrop
    """
    
    # Country filters
    country = NumberFilter(field_name='country__id')
    country_name = CharFilter(field_name='country__name', lookup_expr='icontains')
    
    # Organism filters
    organism = NumberFilter(field_name='organism__id')
    organism_name = CharFilter(field_name='organism__common_name', lookup_expr='icontains')
    
    # GEd Potential filters
    ged_potential = ChoiceFilter(
        field_name='ged_potential',
        choices=NationalPriorityCrop.GED_POTENTIAL_CHOICES
    )
    
    # Production filters
    min_actual = NumberFilter(field_name='actual_production_value', lookup_expr='gte')
    max_actual = NumberFilter(field_name='actual_production_value', lookup_expr='lte')
    min_expected = NumberFilter(field_name='expected_production_value', lookup_expr='gte')
    max_expected = NumberFilter(field_name='expected_production_value', lookup_expr='lte')
    
    # Production gap filter
    has_production_gap = BooleanFilter(method='filter_has_production_gap')
    
    # Production year
    production_year = NumberFilter(field_name='production_year')
    
    # Status filters
    is_active = BooleanFilter()
    
    # Search across multiple fields
    search = CharFilter(method='filter_search')
    
    class Meta:
        model = NationalPriorityCrop
        fields = [
            'country',
            'country_name',
            'organism',
            'organism_name',
            'ged_potential',
            'is_active',
            'production_year',
            'min_actual',
            'max_actual',
            'min_expected',
            'max_expected',
            'has_production_gap',
            'search'
        ]
    
    def filter_has_production_gap(self, queryset, name, value):
        """Filter crops with positive production gap (expected > actual)"""
        if value is True:
            return queryset.filter(
                expected_production_value__gt=models.F('actual_production_value')
            )
        return queryset
    
    def filter_search(self, queryset, name, value):
        """Search across multiple fields"""
        if not value:
            return queryset
        
        return queryset.filter(
            models.Q(organism__common_name__icontains=value) |
            models.Q(organism__scientific_name__icontains=value) |
            models.Q(country__name__icontains=value) |
            models.Q(trait_improvement__icontains=value) |
            models.Q(socio_economic_importance__icontains=value) |
            models.Q(existing_rd__icontains=value)
        )


class NationalPriorityCropAPIFilter(FilterSet):
    """
    Minimal filter set for API endpoints
    """
    
    country = NumberFilter(field_name='country__id')
    organism = NumberFilter(field_name='organism__id')
    ged_potential = ChoiceFilter(choices=NationalPriorityCrop.GED_POTENTIAL_CHOICES)
    is_active = BooleanFilter()
    search = CharFilter(method='filter_search')
    
    class Meta:
        model = NationalPriorityCrop
        fields = [
            'country',
            'organism',
            'ged_potential',
            'is_active',
            'search'
        ]
    
    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            models.Q(organism__common_name__icontains=value) |
            models.Q(organism__scientific_name__icontains=value) |
            models.Q(country__name__icontains=value) |
            models.Q(trait_improvement__icontains=value)
              )
