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

urlpatterns = [
    path('', include(router.urls)),
]