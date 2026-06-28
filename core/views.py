# core/views.py

from django.db.models import Q, Count, Avg, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone

# Django Filter Imports
from django_filters.rest_framework import DjangoFilterBackend

# Django REST Framework Imports
from rest_framework import viewsets, status
from rest_framework import filters as drf_filters  # Aliased to prevent conflicts
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny

from .models import *
from .serializers import *
from .filters import *


# ============= REGION VIEWSET =============

class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for African regions.
    
    Returns a list of all regions with their countries.
    """
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['order', 'name']
    
    @action(detail=True, methods=['get'])
    def countries(self, request, pk=None):
        """Get all countries in a specific region"""
        region = self.get_object()
        countries = region.countries.all()
        serializer = CountryListSerializer(countries, many=True)
        return Response(serializer.data)


# ============= COUNTRY VIEWSET =============

class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for African countries.
    
    Provides detailed information about each country's genome editing landscape,
    including regulatory status, readiness score, and key metrics.
    """
    queryset = Country.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = CountryFilter
    search_fields = ['name', 'code', 'capital']
    ordering_fields = ['name', 'readiness_score', 'active_projects']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CountryListSerializer
        return CountryDetailSerializer
    
    @action(detail=True, methods=['get'])
    def projects(self, request, pk=None):
        """Get all projects in a specific country"""
        country = self.get_object()
        projects = country.projects.all()
        serializer = ProjectListSerializer(projects, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def publications(self, request, pk=None):
        """Get all publications from a specific country"""
        country = self.get_object()
        publications = country.publications.all()
        serializer = PublicationListSerializer(publications, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def experts(self, request, pk=None):
        """Get all experts from a specific country"""
        country = self.get_object()
        experts = country.experts.filter(is_verified=True)
        serializer = ExpertListSerializer(experts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def organisms(self, request, pk=None):
        """Get all organisms used in projects from a specific country"""
        country = self.get_object()
        organisms = Organism.objects.filter(projects__country=country).distinct()
        serializer = OrganismListSerializer(organisms, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get summary statistics for all countries"""
        total_countries = Country.objects.count()
        avg_readiness = Country.objects.aggregate(Avg('readiness_score'))['readiness_score__avg']
        
        stats = {
            'total_countries': total_countries,
            'avg_readiness_score': round(avg_readiness or 0, 2),
            'countries_by_status': dict(Country.objects.values_list('biosafety_status')
                                        .annotate(count=Count('id'))),
            'top_countries_by_projects': list(Country.objects.values('name', 'active_projects')
                                               .order_by('-active_projects')[:5]),
        }
        return Response(stats)


# ============= INSTITUTION VIEWSET =============

class InstitutionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for institutions (research centers, regulatory bodies, universities).
    """
    queryset = Institution.objects.filter(is_active=True)
    serializer_class = InstitutionSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_fields = ['type', 'countries']
    search_fields = ['name', 'acronym', 'description']
    ordering_fields = ['name']
    
    @action(detail=True, methods=['get'])
    def projects(self, request, pk=None):
        """Get projects led by this institution"""
        institution = self.get_object()
        projects = institution.lead_projects.all()
        serializer = ProjectListSerializer(projects, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def experts(self, request, pk=None):
        """Get experts affiliated with this institution"""
        institution = self.get_object()
        experts = institution.experts.filter(is_verified=True)
        serializer = ExpertListSerializer(experts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def protocols(self, request, pk=None):
        """Get protocols from this institution"""
        institution = self.get_object()
        protocols = institution.protocols.all()
        serializer = ProtocolListSerializer(protocols, many=True)
        return Response(serializer.data)


# ============= EXPERT VIEWSET =============

class ExpertViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for genome editing experts and researchers.
    
    Returns verified experts with filtering by sector, country, and expertise.
    """
    queryset = Expert.objects.filter(is_verified=True)
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = ExpertFilter
    search_fields = ['name', 'bio', 'institution__name', 'title']
    ordering_fields = ['name', 'publications_count']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ExpertListSerializer
        return ExpertDetailSerializer
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured experts (for homepage)"""
        featured = self.get_queryset().filter(is_featured=True)[:6]
        serializer = ExpertListSerializer(featured, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def publications(self, request, pk=None):
        """Get publications by this expert"""
        expert = self.get_object()
        publications = Publication.objects.filter(authors__icontains=expert.name)
        serializer = PublicationListSerializer(publications, many=True)
        return Response(serializer.data)


# ============= ORGANISM VIEWSETS =============

class OrganismCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for organism categories (Plant, Animal, Micro-organism, etc.)
    
    Returns categories with their associated organisms count and styling information.
    """
    queryset = OrganismCategory.objects.filter(is_active=True)
    serializer_class = OrganismCategorySerializer
    permission_classes = [AllowAny]
    filter_backends = [drf_filters.SearchFilter, drf_filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['order', 'name']
    
    @action(detail=True, methods=['get'])
    def organisms(self, request, pk=None):
        """Get all organisms in a specific category"""
        category = self.get_object()
        organisms = category.organisms.filter(is_active=True)
        serializer = OrganismListSerializer(organisms, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def with_counts(self, request):
        """Get all categories with organism counts"""
        categories = self.get_queryset()
        data = []
        for cat in categories:
            cat_data = OrganismCategorySerializer(cat).data
            cat_data['organisms'] = OrganismListSerializer(
                cat.organisms.filter(is_active=True), many=True
            ).data
            data.append(cat_data)
        return Response(data)


class OrganismViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for organisms used in genome editing projects.
    
    Includes plants, animals, and micro-organisms with filtering by category,
    featured status, and genome size.
    """
    queryset = Organism.objects.filter(is_active=True)
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = OrganismFilter
    search_fields = ['common_name', 'scientific_name', 'custom_name', 'description']
    ordering_fields = ['common_name', 'genome_size_mb', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OrganismListSerializer
        return OrganismDetailSerializer
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get organisms grouped by category"""
        categories = OrganismCategory.objects.filter(is_active=True)
        result = {}
        for category in categories:
            organisms = self.get_queryset().filter(category=category)
            result[category.name] = {
                'category_id': category.id,
                'category_icon': category.icon,
                'category_color': category.color_code,
                'organisms': OrganismListSerializer(organisms, many=True).data
            }
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured organisms (for homepage)"""
        featured = self.get_queryset().filter(is_featured=True)[:12]
        serializer = OrganismListSerializer(featured, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def projects(self, request, pk=None):
        """Get all projects using this organism"""
        organism = self.get_object()
        projects = organism.projects.all()
        
        status_param = request.query_params.get('status')
        if status_param:
            projects = projects.filter(status=status_param)
        
        country = request.query_params.get('country')
        if country:
            projects = projects.filter(country__code=country)
        
        serializer = ProjectListSerializer(projects, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get statistics for this organism"""
        organism = self.get_object()
        projects = organism.projects.all()
        
        stats = {
            'organism_id': organism.id,
            'organism_name': str(organism),
            'total_projects': projects.count(),
            'projects_by_status': dict(projects.values_list('status').annotate(count=Count('id'))),
            'projects_by_country': list(projects.values('country__name')
                                        .annotate(count=Count('id'))[:10]),
            'projects_by_technology': dict(projects.values_list('technology')
                                           .annotate(count=Count('id'))),
        }
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def search_by_trait(self, request):
        """Search organisms by common editing traits"""
        trait = request.query_params.get('trait', '')
        if not trait:
            return Response({'error': 'Please provide a trait parameter'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        organisms = self.get_queryset().filter(common_traits__contains=[trait])
        serializer = OrganismListSerializer(organisms, many=True)
        return Response(serializer.data)


# ============= PROJECT VIEWSETS =============

class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for genome editing projects.
    
    Returns projects with filtering by status, technology, country, and organism.
    """
    queryset = Project.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = ProjectFilter
    search_fields = ['title', 'description', 'tags']
    ordering_fields = ['start_year', 'title', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProjectCreateUpdateSerializer
        return ProjectDetailSerializer
    
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """Get projects grouped by status"""
        statuses = dict(Project.STATUS_CHOICES)
        result = {}
        for status_code, status_name in statuses.items():
            projects = self.get_queryset().filter(status=status_code)
            result[status_code] = {
                'name': status_name,
                'count': projects.count(),
                'projects': ProjectListSerializer(projects, many=True).data
            }
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def by_technology(self, request):
        """Get projects grouped by technology"""
        technologies = dict(Project.TECH_CHOICES)
        result = {}
        for tech_code, tech_name in technologies.items():
            projects = self.get_queryset().filter(technology=tech_code)
            result[tech_code] = {
                'name': tech_name,
                'count': projects.count(),
                'projects': ProjectListSerializer(projects, many=True).data
            }
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def by_organism(self, request):
        """Get projects grouped by primary organism"""
        organisms = Organism.objects.filter(projects__isnull=False).distinct()
        result = {}
        for organism in organisms:
            projects = self.get_queryset().filter(primary_organism=organism)
            result[organism.id] = {
                'organism_name': str(organism),
                'count': projects.count(),
                'projects': ProjectListSerializer(projects, many=True).data
            }
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get comprehensive project statistics"""
        queryset = self.get_queryset()
        
        stats = {
            'total_projects': queryset.count(),
            'total_cfts': queryset.filter(status='cft').count(),
            'total_commercial': queryset.filter(status='commercial').count(),
            'by_status': dict(queryset.values_list('status').annotate(count=Count('id'))),
            'by_technology': dict(queryset.values_list('technology').annotate(count=Count('id'))),
            'by_sector': dict(queryset.values_list('sector').annotate(count=Count('id'))),
            'by_country': list(queryset.values('country__name').annotate(count=Count('id')).order_by('-count')[:10]),
            'by_organism': list(queryset.values('primary_organism__common_name')
                               .annotate(count=Count('id')).order_by('-count')[:10]),
            'total_funding': queryset.aggregate(total=Sum('funding_amount'))['total'] or 0,
            'active_projects': queryset.exclude(status__in=['completed', 'suspended']).count(),
        }
        return Response(stats)
    
    @action(detail=True, methods=['get'])
    def similar_projects(self, request, pk=None):
        """Find similar projects based on country, technology, or organisms"""
        project = self.get_object()
        
        similar = Project.objects.filter(
            Q(country=project.country) |
            Q(technology=project.technology) |
            Q(organisms__in=project.organisms.all())
        ).exclude(id=project.id).distinct()[:10]
        
        serializer = ProjectListSerializer(similar, many=True)
        return Response(serializer.data)


# ============= PUBLICATION VIEWSET =============

class PublicationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for publications, reports, and policy briefs.
    """
    queryset = Publication.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = PublicationFilter
    search_fields = ['title', 'authors', 'abstract', 'keywords']
    ordering_fields = ['-year', 'downloads']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PublicationListSerializer
        return PublicationDetailSerializer
    
    @action(detail=True, methods=['post'])
    def download(self, request, pk=None):
        """Increment download counter for a publication"""
        publication = self.get_object()
        publication.downloads += 1
        publication.save()
        return Response({
            'downloads': publication.downloads,
            'message': 'Download counted successfully'
        })
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured publications (for homepage)"""
        featured = self.get_queryset().filter(is_featured=True)[:10]
        serializer = PublicationListSerializer(featured, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_year(self, request):
        """Get publications grouped by year"""
        years = self.get_queryset().values_list('year', flat=True).distinct().order_by('-year')
        result = {}
        for year in years:
            pubs = self.get_queryset().filter(year=year)
            result[year] = {
                'count': pubs.count(),
                'publications': PublicationListSerializer(pubs, many=True).data
            }
        return Response(result)


# ============= PROTOCOL VIEWSET =============

class ProtocolViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for laboratory protocols, SOPs, and technical guides.
    """
    queryset = Protocol.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = ProtocolFilter
    search_fields = ['title', 'description', 'materials', 'steps']
    ordering_fields = ['-downloads', '-rating']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProtocolListSerializer
        return ProtocolDetailSerializer
    
    @action(detail=True, methods=['post'])
    def download(self, request, pk=None):
        """Increment download counter for a protocol"""
        protocol = self.get_object()
        protocol.downloads += 1
        protocol.save()
        return Response({
            'downloads': protocol.downloads,
            'message': 'Download counted successfully'
        })
    
    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        """Rate a protocol (1-5 stars)"""
        protocol = self.get_object()
        rating = request.data.get('rating')
        
        if not rating or not (1 <= rating <= 5):
            return Response({'error': 'Rating must be between 1 and 5'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        total_rating = protocol.rating * protocol.rating_count + rating
        protocol.rating_count += 1
        protocol.rating = total_rating / protocol.rating_count
        protocol.save()
        
        return Response({
            'rating': protocol.rating,
            'rating_count': protocol.rating_count,
            'message': 'Thank you for rating!'
        })
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured protocols (for homepage)"""
        featured = self.get_queryset().filter(is_featured=True)[:6]
        serializer = ProtocolListSerializer(featured, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def top_rated(self, request):
        """Get top rated protocols"""
        top = self.get_queryset().filter(rating_count__gt=0).order_by('-rating')[:10]
        serializer = ProtocolListSerializer(top, many=True)
        return Response(serializer.data)


# ============= CONSULTATION VIEWSET =============

class ConsultationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for public consultations on genome editing policies.
    """
    queryset = Consultation.objects.all()
    serializer_class = ConsultationSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter]
    filterset_fields = ['status', 'country']
    search_fields = ['title', 'description']
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit a response to an open consultation"""
        consultation = self.get_object()
        
        if consultation.status != 'open' or consultation.closing_date < timezone.now().date():
            return Response({'error': 'This consultation is no longer accepting submissions'},
                          status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ConsultationSubmissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(consultation=consultation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def open(self, request):
        """Get all open consultations"""
        open_consultations = self.get_queryset().filter(
            status='open',
            closing_date__gte=timezone.now().date()
        )
        serializer = self.get_serializer(open_consultations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def closing_soon(self, request):
        """Get consultations closing within 7 days"""
        seven_days_from_now = timezone.now().date() + timezone.timedelta(days=7)
        closing_soon = self.get_queryset().filter(
            status='open',
            closing_date__lte=seven_days_from_now,
            closing_date__gte=timezone.now().date()
        )
        serializer = self.get_serializer(closing_soon, many=True)
        return Response(serializer.data)


# ============= NEWS VIEWSET =============

class NewsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for news articles and announcements.
    """
    queryset = News.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [drf_filters.SearchFilter, drf_filters.OrderingFilter]
    search_fields = ['title', 'summary', 'content']
    ordering_fields = ['-published_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return NewsListSerializer
        return NewsDetailSerializer
    
    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        """Increment view counter for a news article"""
        news = self.get_object()
        news.views += 1
        news.save()
        return Response({'views': news.views})
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured news articles (for homepage)"""
        featured = self.get_queryset().filter(is_featured=True)[:5]
        serializer = NewsListSerializer(featured, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest news articles"""
        latest = self.get_queryset().order_by('-published_date')[:10]
        serializer = NewsListSerializer(latest, many=True)
        return Response(serializer.data)


# ============= FAQ VIEWSET =============

class FAQViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for frequently asked questions.
    """
    queryset = FAQ.objects.filter(is_published=True)
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]
    filter_backends = [drf_filters.OrderingFilter]
    ordering_fields = ['order', 'category']
    filterset_fields = ['category']
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get FAQs grouped by category"""
        categories = dict(FAQ.CATEGORY_CHOICES)
        result = {}
        for cat_code, cat_name in categories.items():
            faqs = self.get_queryset().filter(category=cat_code)
            result[cat_code] = {
                'name': cat_name,
                'count': faqs.count(),
                'faqs': FAQSerializer(faqs, many=True).data
            }
        return Response(result)


# ============= GLOSSARY VIEWSET =============

class GlossaryTermViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for glossary terms.
    """
    queryset = GlossaryTerm.objects.all()
    serializer_class = GlossaryTermSerializer
    permission_classes = [AllowAny]
    filter_backends = [drf_filters.SearchFilter, drf_filters.OrderingFilter]
    search_fields = ['term', 'definition']
    ordering_fields = ['term']
    filterset_fields = ['category']


# ============= FUNDING VIEWSET =============

class FundingOpportunityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for funding and grant opportunities.
    """
    queryset = FundingOpportunity.objects.all()
    serializer_class = FundingOpportunitySerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['title', 'description', 'donor']
    ordering_fields = ['deadline']
    
    @action(detail=False, methods=['get'])
    def open(self, request):
        """Get open funding opportunities"""
        open_opportunities = self.get_queryset().filter(
            status__in=['open', 'closing_soon'],
            deadline__gte=timezone.now().date()
        )
        serializer = self.get_serializer(open_opportunities, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def closing_soon(self, request):
        """Get funding opportunities closing within 14 days"""
        fourteen_days_from_now = timezone.now().date() + timezone.timedelta(days=14)
        closing_soon = self.get_queryset().filter(
            status__in=['open', 'closing_soon'],
            deadline__lte=fourteen_days_from_now,
            deadline__gte=timezone.now().date()
        )
        serializer = self.get_serializer(closing_soon, many=True)
        return Response(serializer.data)


# ============= EVENT VIEWSET =============

class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for workshops, conferences, and training events.
    """
    queryset = Event.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = EventFilter
    search_fields = ['title', 'description', 'venue']
    ordering_fields = ['start_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EventListSerializer
        return EventDetailSerializer
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming events"""
        upcoming = self.get_queryset().filter(start_date__gte=timezone.now()).order_by('start_date')[:10]
        serializer = EventListSerializer(upcoming, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured events"""
        featured = self.get_queryset().filter(is_featured=True, start_date__gte=timezone.now()).order_by('start_date')[:5]
        serializer = EventListSerializer(featured, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_country(self, request):
        """Get upcoming events by country"""
        country_code = request.query_params.get('country')
        if not country_code:
            return Response({'error': 'Please provide country parameter'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        events = self.get_queryset().filter(
            country__code=country_code,
            start_date__gte=timezone.now()
        ).order_by('start_date')
        
        serializer = EventListSerializer(events, many=True)
        return Response(serializer.data)


# ============= DASHBOARD VIEWSET =============

class DashboardViewSet(viewsets.GenericViewSet):
    """
    API endpoint for dashboard statistics and analytics.
    """
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get overall portal statistics"""
        stats = {
            'total_countries': Country.objects.count(),
            'total_projects': Project.objects.count(),
            'total_publications': Publication.objects.count(),
            'total_experts': Expert.objects.filter(is_verified=True).count(),
            'total_protocols': Protocol.objects.count(),
            'total_organisms': Organism.objects.filter(is_active=True).count(),
            'total_events': Event.objects.filter(start_date__gte=timezone.now()).count(),
            'open_consultations': Consultation.objects.filter(
                status='open',
                closing_date__gte=timezone.now().date()
            ).count(),
            'open_funding': FundingOpportunity.objects.filter(
                status__in=['open', 'closing_soon']
            ).count(),
            'featured_news': News.objects.filter(is_featured=True).count(),
        }
        return Response(stats)


# ============= REGULATORY FRAMEWORK VIEWSETS =============

class RegulatoryFrameworkViewSet(viewsets.ModelViewSet):
    """
    API endpoint for regulatory frameworks for genome editing in Africa.
    
    Provides detailed information about each country's regulatory framework,
    including institutions, instruments, multilateral agreements, and status.
    """
    queryset = RegulatoryFramework.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_fields = ['status', 'approach', 'country__region']
    search_fields = ['country__name', 'summary', 'country__code']
    ordering_fields = ['country__name', 'status', 'last_updated']

    def get_serializer_class(self):
        if self.action == 'list':
            return RegulatoryFrameworkListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return RegulatoryFrameworkCreateUpdateSerializer
        return RegulatoryFrameworkDetailSerializer

    @action(detail=False, methods=['get'])
    def by_country(self, request):
        """Get regulatory framework by country code or name"""
        country_code = request.query_params.get('code')
        country_name = request.query_params.get('name')
        
        if country_code:
            framework = RegulatoryFramework.objects.filter(country__code__iexact=country_code).first()
        elif country_name:
            framework = RegulatoryFramework.objects.filter(country__name__iexact=country_name).first()
        else:
            return Response(
                {'error': 'Please provide either code or name parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not framework:
            return Response(
                {'error': 'Regulatory framework not found for the specified country'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(framework)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get statistics about regulatory frameworks"""
        total_countries = RegulatoryFramework.objects.count()
        by_status = dict(
            RegulatoryFramework.objects.values_list('status')
            .annotate(count=Count('id'))
        )
        by_approach = dict(
            RegulatoryFramework.objects.values_list('approach')
            .annotate(count=Count('id'))
        )
        
        stats = {
            'total_frameworks': total_countries,
            'by_status': by_status,
            'by_approach': by_approach,
            'functional_frameworks': RegulatoryFramework.objects.filter(
                status__in=['functional', 'implemented']
            ).count(),
            'with_guidelines': RegulatoryFramework.objects.filter(
                ged_guidelines_date__isnull=False
            ).count(),
        }
        return Response(stats)

    @action(detail=True, methods=['get'])
    def agreements(self, request, pk=None):
        """Get all multilateral agreements for a country"""
        framework = self.get_object()
        agreements = framework.multilateral_agreements.filter(is_active=True)
        serializer = MultilateralAgreementSerializer(agreements, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def institutions(self, request, pk=None):
        """Get all regulatory institutions for a country"""
        framework = self.get_object()
        institutions = framework.regulatory_institutions.filter(is_active=True)
        serializer = RegulatoryInstitutionSerializer(institutions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def instruments(self, request, pk=None):
        """Get all regulatory instruments for a country"""
        framework = self.get_object()
        instruments = framework.regulatory_instruments.filter(is_current=True)
        serializer = RegulatoryInstrumentSerializer(instruments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def timeline(self, request, pk=None):
        """Get regulatory timeline for a country"""
        framework = self.get_object()
        timeline = framework.regulatory_timeline.all()
        serializer = RegulatoryTimelineSerializer(timeline, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def ged_status(self, request, pk=None):
        """Get genome editing regulatory status for a country"""
        framework = self.get_object()
        statuses = framework.ged_regulatory_statuses.all()
        serializer = GedRegulatoryStatusSerializer(statuses, many=True)
        return Response(serializer.data)


class MultilateralAgreementViewSet(viewsets.ModelViewSet):
    """
    API endpoint for multilateral agreements
    """
    queryset = MultilateralAgreement.objects.all()
    serializer_class = MultilateralAgreementSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter]
    filterset_fields = ['agreement_type', 'framework__country']
    search_fields = ['name', 'framework__country__name']


class RegulatoryInstitutionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for regulatory institutions
    """
    queryset = RegulatoryInstitution.objects.filter(is_active=True)
    serializer_class = RegulatoryInstitutionSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter]
    filterset_fields = ['role', 'framework__country', 'institution']
    search_fields = ['institution__name', 'mandate']


class RegulatoryInstrumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for regulatory instruments
    """
    queryset = RegulatoryInstrument.objects.filter(is_current=True)
    serializer_class = RegulatoryInstrumentSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter]
    filterset_fields = ['instrument_type', 'coverage', 'framework__country']
    search_fields = ['title', 'summary']


class GedRegulatoryStatusViewSet(viewsets.ModelViewSet):
    """
    API endpoint for genome editing regulatory statuses
    """
    queryset = GedRegulatoryStatus.objects.all()
    serializer_class = GedRegulatoryStatusSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter]
    filterset_fields = ['category', 'status', 'framework__country']
    search_fields = ['description']


class RegulatoryTimelineViewSet(viewsets.ModelViewSet):
    """
    API endpoint for regulatory timelines
    """
    queryset = RegulatoryTimeline.objects.all()
    serializer_class = RegulatoryTimelineSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, drf_filters.OrderingFilter]
    filterset_fields = ['event_type', 'framework__country']
    ordering_fields = ['event_date']


# ============= INFRASTRUCTURE & EQUIPMENT VIEWSETS =============

class InfrastructureCategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for infrastructure categories
    """
    queryset = InfrastructureCategory.objects.filter(is_active=True)
    serializer_class = InfrastructureCategorySerializer
    permission_classes = [AllowAny]
    filter_backends = [drf_filters.SearchFilter, drf_filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['order', 'name']


class LaboratoryFacilityFilter(filters.FilterSet):
    """
    Filter for LaboratoryFacility model
    """
    biosafety_level = filters.MultipleChoiceFilter(
        choices=LaboratoryFacility.BIOSAFETY_LEVELS,
        field_name='biosafety_level',
        lookup_expr='icontains'
    )
    status = filters.MultipleChoiceFilter(
        choices=LaboratoryFacility.STATUS_CHOICES
    )
    category = filters.NumberFilter(field_name='category__id')
    institution = filters.NumberFilter(field_name='institution__id')
    country = filters.NumberFilter(field_name='institution__country__id')
    search = filters.CharFilter(method='filter_search')
    is_active = filters.BooleanFilter()
    
    class Meta:
        model = LaboratoryFacility
        fields = {
            'status': ['exact'],
            'biosafety_level': ['icontains', 'exact'],
            'category': ['exact'],
            'institution': ['exact'],
            'is_active': ['exact'],
        }
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(name__icontains=value) |
            models.Q(abbreviation__icontains=value) |
            models.Q(institution__name__icontains=value) |
            models.Q(description__icontains=value) |
            models.Q(facility_type__icontains=value)
        )


class LaboratoryFacilityViewSet(viewsets.ModelViewSet):
    """
    API endpoint for laboratory facilities
    """
    queryset = LaboratoryFacility.objects.filter(is_active=True)
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = LaboratoryFacilityFilter
    search_fields = ['name', 'abbreviation', 'institution__name', 'country__name', 'facility_type', 'description']
    ordering_fields = ['institution__name', 'country__name', 'name', 'status', 'created_at']




    def get_serializer_class(self):
        if self.action == 'list':
            return LaboratoryFacilityListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return LaboratoryFacilityCreateUpdateSerializer
        return LaboratoryFacilityDetailSerializer

    @action(detail=False, methods=['get'])
    def by_country(self, request):
        """Get laboratory facilities by country"""
        country_code = request.query_params.get('code')
        country_name = request.query_params.get('name')
        
        if country_code:
            facilities = self.get_queryset().filter(
                country__code__iexact=country_code
            )
        elif country_name:
            facilities = self.get_queryset().filter(
                country__name__iexact=country_name
            )
        else:
            return Response(
                {'error': 'Please provide either code or name parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = LaboratoryFacilityListSerializer(facilities, many=True)
        return Response(serializer.data)





    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get statistics about laboratory facilities"""
        total = LaboratoryFacility.objects.filter(is_active=True).count()
        
        by_status = dict(
            LaboratoryFacility.objects.filter(is_active=True)
            .values_list('status')
            .annotate(count=Count('id'))
        )
        
        # Handle MultiSelectField for biosafety_level
        biosafety_counts = {}
        for level, label in LaboratoryFacility.BIOSAFETY_LEVELS:
            count = LaboratoryFacility.objects.filter(
                is_active=True,
                biosafety_level__icontains=level
            ).count()
            if count > 0:
                biosafety_counts[level] = count
        
        by_category = dict(
            LaboratoryFacility.objects.filter(is_active=True)
            .values_list('category__name')
            .annotate(count=Count('id'))
        )
        
        # Country counts - now using direct country field
        by_country = list(
            LaboratoryFacility.objects.filter(is_active=True)
            .values('country__name')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
        




        stats = {
            'total_facilities': total,
            'by_status': by_status,
            'by_biosafety_level': biosafety_counts,
            'by_category': by_category,
            'by_country': by_country,  
            'fully_equipped': LaboratoryFacility.objects.filter(
                is_active=True, status='fully_equipped'
            ).count(),
            'partially_equipped': LaboratoryFacility.objects.filter(
                is_active=True, status='partially_equipped'
            ).count(),
        }
        return Response(stats)

    @action(detail=True, methods=['get'])
    def equipment(self, request, pk=None):
        """Get equipment for a specific facility"""
        facility = self.get_object()
        equipment = facility.equipment.filter(is_active=True)
        serializer = EquipmentSerializer(equipment, many=True)
        return Response(serializer.data)


class EquipmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for equipment
    """
    queryset = Equipment.objects.filter(is_active=True)
    serializer_class = EquipmentSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_fields = ['equipment_type', 'status', 'condition', 'facility']
    search_fields = ['name', 'model', 'manufacturer', 'serial_number']
    ordering_fields = ['name', 'acquisition_date']

    @action(detail=False, methods=['get'])
    def by_country(self, request):
        """Get equipment by country"""
        country_code = request.query_params.get('code')
        if country_code:
            equipment = self.get_queryset().filter(
                facility__institution__country__code__iexact=country_code
            )
            serializer = self.get_serializer(equipment, many=True)
            return Response(serializer.data)
        return Response(
            {'error': 'Please provide country code parameter'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get statistics about equipment"""
        total = Equipment.objects.filter(is_active=True).count()
        by_type = dict(
            Equipment.objects.filter(is_active=True)
            .values_list('equipment_type')
            .annotate(count=Count('id'))
        )
        by_status = dict(
            Equipment.objects.filter(is_active=True)
            .values_list('status')
            .annotate(count=Count('id'))
        )
        
        stats = {
            'total_equipment': total,
            'by_type': by_type,
            'by_status': by_status,
            'operational': Equipment.objects.filter(
                is_active=True, status='operational'
            ).count(),
            'needs_repair': Equipment.objects.filter(
                is_active=True, status__in=['needs_repair', 'under_maintenance']
            ).count(),
        }
        return Response(stats)


class InfrastructureProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint for infrastructure projects
    """
    queryset = InfrastructureProject.objects.filter(is_active=True)
    serializer_class = InfrastructureProjectSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'country', 'institution']
    search_fields = ['title', 'description', 'objectives']
    ordering_fields = ['start_date', 'end_date', 'priority']

    @action(detail=False, methods=['get'])
    def by_country(self, request):
        """Get infrastructure projects by country"""
        country_code = request.query_params.get('code')
        if country_code:
            projects = self.get_queryset().filter(country__code__iexact=country_code)
            serializer = self.get_serializer(projects, many=True)
            return Response(serializer.data)
        return Response(
            {'error': 'Please provide country code parameter'},
            status=status.HTTP_400_BAD_REQUEST
        )


class TrainingCapacityViewSet(viewsets.ModelViewSet):
    """
    API endpoint for training capacities
    """
    queryset = TrainingCapacity.objects.filter(is_active=True)
    serializer_class = TrainingCapacitySerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_fields = ['training_type', 'skill_level', 'institution']
    search_fields = ['title', 'description', 'institution__name']
    ordering_fields = ['start_date', 'title']

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured training capacities"""
        featured = self.get_queryset().filter(is_featured=True)[:6]
        serializer = self.get_serializer(featured, many=True)
        return Response(serializer.data)


class InfrastructureAssessmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for infrastructure assessments
    """
    queryset = InfrastructureAssessment.objects.all()
    serializer_class = InfrastructureAssessmentSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_fields = ['assessment_area', 'priority', 'country']
    search_fields = ['title', 'description']
    ordering_fields = ['-assessment_date']

    @action(detail=False, methods=['get'])
    def by_country(self, request):
        """Get infrastructure assessments by country"""
        country_code = request.query_params.get('code')
        if country_code:
            assessments = self.get_queryset().filter(country__code__iexact=country_code)
            serializer = self.get_serializer(assessments, many=True)
            return Response(serializer.data)
        return Response(
            {'error': 'Please provide country code parameter'},
            status=status.HTTP_400_BAD_REQUEST
        )
