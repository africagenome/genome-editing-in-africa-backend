# core/admin.py

from django.contrib import admin
from django.utils.html import format_html
from import_export.admin import ExportActionMixin
from .models import (
    Region, Country, Institution, Expert, Project, Publication,
    Protocol, Consultation, ConsultationSubmission, News, FAQ,
    GlossaryTerm, FundingOpportunity, Event, OrganismCategory, Organism
)


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'order']
    search_fields = ['name', 'code']
    list_editable = ['order']


@admin.register(Country)
class CountryAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ['name', 'code', 'region', 'biosafety_status', 
                    'readiness_score', 'active_projects']
    list_filter = ['region', 'biosafety_status', 'classification_approach']
    search_fields = ['name', 'code', 'capital']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ['name', 'acronym', 'type', 'country', 'is_active']
    list_filter = ['type', 'country', 'is_active']
    search_fields = ['name', 'acronym', 'description']
    list_editable = ['is_active']


@admin.register(Expert)
class ExpertAdmin(admin.ModelAdmin):
    list_display = ['name', 'title', 'institution', 'country', 'sector', 'is_verified', 'is_featured']
    list_filter = ['sector', 'country', 'is_verified', 'is_featured']
    search_fields = ['name', 'email', 'institution__name']
    list_editable = ['is_verified', 'is_featured']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'country', 'technology', 'status', 'start_year']
    list_filter = ['status', 'technology', 'sector', 'country']
    search_fields = ['title', 'description']
    filter_horizontal = ['partners']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ['title', 'authors', 'year', 'type', 'topic', 'downloads']
    list_filter = ['type', 'topic', 'year', 'language', 'is_featured']
    search_fields = ['title', 'authors', 'abstract', 'doi']
    readonly_fields = ['downloads', 'created_at']


@admin.register(Protocol)
class ProtocolAdmin(admin.ModelAdmin):
    list_display = ['title', 'technology', 'protocol_type', 'difficulty', 'downloads', 'rating']
    list_filter = ['technology', 'protocol_type', 'difficulty', 'is_featured']
    search_fields = ['title', 'description']
    readonly_fields = ['downloads', 'rating', 'rating_count']


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ['title', 'country', 'opening_date', 'closing_date', 'status']
    list_filter = ['status', 'country']
    search_fields = ['title', 'description']
    date_hierarchy = 'opening_date'


@admin.register(ConsultationSubmission)
class ConsultationSubmissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'consultation', 'stakeholder_type', 'submitted_at', 'is_approved']
    list_filter = ['stakeholder_type', 'consultation', 'is_approved']
    search_fields = ['name', 'email', 'organization']


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'published_date', 'is_featured', 'views']
    list_filter = ['is_featured', 'published_date']
    search_fields = ['title', 'summary']
    prepopulated_fields = {'slug': ['title']}
    filter_horizontal = ['countries']
    readonly_fields = ['views', 'created_at', 'updated_at']


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'order', 'is_published']
    list_filter = ['category', 'is_published']
    search_fields = ['question', 'answer']
    list_editable = ['order', 'is_published']


@admin.register(GlossaryTerm)
class GlossaryTermAdmin(admin.ModelAdmin):
    list_display = ['term', 'abbreviation', 'category']
    list_filter = ['category']
    search_fields = ['term', 'definition']
    filter_horizontal = ['related_terms']


@admin.register(FundingOpportunity)
class FundingOpportunityAdmin(admin.ModelAdmin):
    list_display = ['title', 'donor', 'deadline', 'status', 'is_featured']
    list_filter = ['status', 'donor', 'is_featured']
    search_fields = ['title', 'description', 'donor']
    filter_horizontal = ['countries_eligible']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'start_date', 'end_date', 'country', 'is_featured']
    list_filter = ['event_type', 'is_virtual', 'is_featured', 'country']
    search_fields = ['title', 'description', 'venue']
    prepopulated_fields = {'slug': ['title']}
    date_hierarchy = 'start_date'


class OrganismInline(admin.TabularInline):
    """Inline for organisms in category admin"""
    model = Organism
    fields = ['common_name', 'scientific_name', 'is_featured', 'is_active']
    extra = 0
    show_change_link = True


@admin.register(OrganismCategory)
class OrganismCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'icon', 'color_code', 'order', 'is_active', 'organism_count']
    list_filter = ['category_type', 'is_active']
    search_fields = ['name', 'description']
    list_editable = ['order', 'is_active', 'icon', 'color_code']
    inlines = [OrganismInline]
    
    def organism_count(self, obj):
        return obj.organisms.count()
    organism_count.short_description = 'Organisms'


@admin.register(Organism)
class OrganismAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'category', 'common_name', 'scientific_name', 'genome_size_mb', 'is_featured', 'is_active']
    list_filter = ['category', 'category__category_type', 'is_featured', 'is_active']
    search_fields = ['common_name', 'scientific_name', 'custom_name', 'description']
    list_editable = ['is_featured', 'is_active']
    filter_horizontal = []
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('common_name', 'scientific_name', 'custom_name', 'category')
        }),
        ('Genome Information', {
            'fields': ('genome_size_mb', 'chromosome_count', 'ploidy'),
            'classes': ('collapse',)
        }),
        ('Description', {
            'fields': ('description', 'native_region', 'economic_importance')
        }),
        ('Media', {
            'fields': ('icon', 'image')
        }),
        ('Traits', {
            'fields': ('common_traits',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']
    
    def display_name(self, obj):
        return str(obj)
    display_name.short_description = 'Name'