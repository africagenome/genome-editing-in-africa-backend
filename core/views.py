from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import (
    Region, Country, Institution, Expert, Project, Publication,
    Protocol, Consultation, ConsultationSubmission, News, FAQ,
    GlossaryTerm, FundingOpportunity, Event, OrganismCategory, Organism
)
from .serializers import (
    RegionSerializer, CountryListSerializer, CountryDetailSerializer,
    InstitutionSerializer, ExpertListSerializer, ExpertDetailSerializer,
    ProjectListSerializer, ProjectDetailSerializer, ProjectCreateUpdateSerializer,
    PublicationListSerializer, PublicationDetailSerializer,
    ProtocolListSerializer, ProtocolDetailSerializer,
    ConsultationSerializer, ConsultationSubmissionSerializer,
    NewsListSerializer, NewsDetailSerializer, FAQSerializer,
    GlossaryTermSerializer, FundingOpportunitySerializer,
    EventListSerializer, EventDetailSerializer,
    OrganismCategorySerializer, OrganismListSerializer, OrganismDetailSerializer,
    DashboardStatsSerializer
)
from .filters import (
    CountryFilter, ProjectFilter, ExpertFilter, PublicationFilter,
    ProtocolFilter, EventFilter, OrganismFilter
)


class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for African regions.
    
    Returns a list of all regions with their countries.
    """
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['order', 'name']
    
    @action(detail=True, methods=['get'])
    def countries(self, request, pk=None):
        """Get all countries in a specific region"""
        region = self.get_object()
        countries = region.countries.all()
        serializer = CountryListSerializer(countries, many=True)
        return Response(serializer.data)


class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for African countries.
    
    Provides detailed information about each country's genome editing landscape,
    including regulatory status, readiness score, and key metrics.
    """
    queryset = Country.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
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


class InstitutionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for institutions (research centers, regulatory bodies, universities).
    """
    queryset = Institution.objects.filter(is_active=True)
    serializer_class = InstitutionSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'country']
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


class ExpertViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for genome editing experts and researchers.
    
    Returns verified experts with filtering by sector, country, and expertise.
    """
    queryset = Expert.objects.filter(is_verified=True)
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
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
        # This would require a many-to-many relationship between Expert and Publication
        # For now, return empty list or filter by author name
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
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
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
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
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
        
        # Apply optional filters
        status = request.query_params.get('status')
        if status:
            projects = projects.filter(status=status)
        
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


# ============= PROJECT VIEWSETS (UPDATED) =============

class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for genome editing projects.
    
    Returns projects with filtering by status, technology, country, and organism.
    """
    queryset = Project.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProjectFilter
    search_fields = ['title', 'description', 'crop_focus', 'tags']
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
        
        # Find projects with same country or same technology or same organisms
        similar = Project.objects.filter(
            Q(country=project.country) |
            Q(technology=project.technology) |
            Q(organisms__in=project.organisms.all())
        ).exclude(id=project.id).distinct()[:10]
        
        serializer = ProjectListSerializer(similar, many=True)
        return Response(serializer.data)


class PublicationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for publications, reports, and policy briefs.
    """
    queryset = Publication.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
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


class ProtocolViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for laboratory protocols, SOPs, and technical guides.
    """
    queryset = Protocol.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
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
        
        # Calculate new average rating
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


class ConsultationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for public consultations on genome editing policies.
    """
    queryset = Consultation.objects.all()
    serializer_class = ConsultationSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'country']
    search_fields = ['title', 'description']
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit a response to an open consultation"""
        consultation = self.get_object()
        
        # Check if consultation is still open
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


class NewsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for news articles and announcements.
    """
    queryset = News.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
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


class FAQViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for frequently asked questions.
    """
    queryset = FAQ.objects.filter(is_published=True)
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.OrderingFilter]
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


class GlossaryTermViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for glossary terms.
    """
    queryset = GlossaryTerm.objects.all()
    serializer_class = GlossaryTermSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['term', 'definition']
    ordering_fields = ['term']
    filterset_fields = ['category']


class FundingOpportunityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for funding and grant opportunities.
    """
    queryset = FundingOpportunity.objects.all()
    serializer_class = FundingOpportunitySerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
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


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for workshops, conferences, and training events.
    """
    queryset = Event.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
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