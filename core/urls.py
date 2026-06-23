from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
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
router.register(r'organism-categories', views.OrganismCategoryViewSet, basename='organism-categories')
router.register(r'organisms', views.OrganismViewSet, basename='organisms')

router.register(r'frameworks', views.RegulatoryFrameworkViewSet, basename='regulatory-frameworks')
router.register(r'agreements', views.MultilateralAgreementViewSet, basename='multilateral-agreements')
router.register(r'institutions', views.RegulatoryInstitutionViewSet, basename='regulatory-institutions')
router.register(r'instruments', views.RegulatoryInstrumentViewSet, basename='regulatory-instruments')
router.register(r'ged-status', views.GedRegulatoryStatusViewSet, basename='ged-regulatory-status')
router.register(r'timeline', views.RegulatoryTimelineViewSet, basename='regulatory-timeline')


router.register(r'categories', views.InfrastructureCategoryViewSet, basename='infrastructure-categories')
router.register(r'facilities', views.LaboratoryFacilityViewSet, basename='laboratory-facilities')
router.register(r'equipment', views.EquipmentViewSet, basename='equipment')
router.register(r'projects', views.InfrastructureProjectViewSet, basename='infrastructure-projects')
router.register(r'training', views.TrainingCapacityViewSet, basename='training-capacity')
router.register(r'assessments', views.InfrastructureAssessmentViewSet, basename='infrastructure-assessments')

urlpatterns = [
    path('', include(router.urls)),
]