from django_filters import rest_framework as filters
from .models import Country, Project, Expert, Publication, Protocol, Event, Organism


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