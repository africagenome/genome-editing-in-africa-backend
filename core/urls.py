# core/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

# ============= CORE ENDPOINTS =============
router.register(r'regions', views.RegionViewSet, basename='regions')
router.register(r'countries', views.CountryViewSet, basename='countries')
router.register(r'institutions', views.InstitutionViewSet, basename='institutions')
router.register(r'experts', views.ExpertViewSet, basename='experts')
router.register(r'projects', views.ProjectViewSet, basename='projects')
router.register(r'publications', views.PublicationViewSet, basename='publications')
router.register(r'protocols', views.ProtocolViewSet, basename='protocols')
router.register(r'consultations', views.ConsultationViewSet, basename='consultations')
router.register(r'news', views.NewsViewSet, basename='news')
router.register(r'faqs', views.FAQViewSet, basename='faqs')
router.register(r'glossary', views.GlossaryTermViewSet, basename='glossary')
router.register(r'funding', views.FundingOpportunityViewSet, basename='funding')
router.register(r'events', views.EventViewSet, basename='events')

# ============= DASHBOARD =============
router.register(r'dashboard', views.DashboardViewSet, basename='dashboard')

# ============= ORGANISM ENDPOINTS =============
router.register(r'organism-categories', views.OrganismCategoryViewSet, basename='organism-categories')
router.register(r'organisms', views.OrganismViewSet, basename='organisms')

# ============= REGULATORY FRAMEWORK ENDPOINTS =============
router.register(r'regulatory-frameworks', views.RegulatoryFrameworkViewSet, basename='regulatory-frameworks')
router.register(r'regulatory-agreements', views.MultilateralAgreementViewSet, basename='regulatory-agreements')
router.register(r'regulatory-institutions', views.RegulatoryInstitutionViewSet, basename='regulatory-institutions')
router.register(r'regulatory-instruments', views.RegulatoryInstrumentViewSet, basename='regulatory-instruments')
router.register(r'regulatory-ged-status', views.GedRegulatoryStatusViewSet, basename='regulatory-ged-status')
router.register(r'regulatory-timelines', views.RegulatoryTimelineViewSet, basename='regulatory-timelines')

# ============= INFRASTRUCTURE & EQUIPMENT ENDPOINTS =============
router.register(r'infrastructure-categories', views.InfrastructureCategoryViewSet, basename='infrastructure-categories')
router.register(r'laboratory-facilities', views.LaboratoryFacilityViewSet, basename='laboratory-facilities')
router.register(r'equipment', views.EquipmentViewSet, basename='equipment')
router.register(r'infrastructure-projects', views.InfrastructureProjectViewSet, basename='infrastructure-projects')
router.register(r'training-capacities', views.TrainingCapacityViewSet, basename='training-capacities')
router.register(r'infrastructure-assessments', views.InfrastructureAssessmentViewSet, basename='infrastructure-assessments')

# ============= NATIONAL PRIORITY CROPS =============
router.register(r'priority-crops', views.NationalPriorityCropViewSet, basename='priority-crops')


urlpatterns = [
    path('', include(router.urls)),
]
