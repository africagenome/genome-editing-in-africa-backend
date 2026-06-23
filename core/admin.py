# core/admin.py

from django.contrib import admin
from django.utils.html import format_html
from import_export.admin import ExportActionMixin
from .models import *


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
    list_display = ['name', 'acronym', 'type', 'display_countries', 'is_active']
    list_filter = ['type', 'countries', 'is_active']
    search_fields = ['name', 'acronym', 'description']
    list_editable = ['is_active']
    filter_horizontal = ('countries',)

    @admin.display(description='Countries')
    def display_countries(self, obj):
        return ", ".join([country.name for country in obj.countries.all()])


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


# ============ REGULATORY FRAMEWORK ADMIN ============

class MultilateralAgreementInline(admin.TabularInline):
    model = MultilateralAgreement
    extra = 1
    fields = ['agreement_type', 'name', 'signed_date', 'ratified_date', 'is_active']


class RegulatoryInstitutionInline(admin.TabularInline):
    model = RegulatoryInstitution
    extra = 1
    fields = ['institution', 'role', 'mandate', 'order', 'is_active']


class RegulatoryInstrumentInline(admin.TabularInline):
    model = RegulatoryInstrument
    extra = 1
    fields = ['title', 'instrument_type', 'date_enacted', 'coverage', 'is_current']


class GedRegulatoryStatusInline(admin.TabularInline):
    model = GedRegulatoryStatus
    extra = 1
    fields = ['category', 'status', 'description']


class RegulatoryTimelineInline(admin.TabularInline):
    model = RegulatoryTimeline
    extra = 1
    fields = ['event_type', 'title', 'description', 'event_date']


@admin.register(RegulatoryFramework)
class RegulatoryFrameworkAdmin(admin.ModelAdmin):
    list_display = ['country', 'status_display_colored', 'approach', 'ged_guidelines_date', 'last_updated']
    list_filter = ['status', 'approach', 'country__region']
    search_fields = ['country__name', 'summary']
    readonly_fields = ['created_at', 'updated_at', 'last_updated']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('country', 'status', 'approach', 'summary')
        }),
        ('Key Dates', {
            'fields': ('biosafety_act_date', 'biosafety_regulations_date', 'ged_guidelines_date')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'last_updated'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [
        MultilateralAgreementInline,
        RegulatoryInstitutionInline,
        RegulatoryInstrumentInline,
        GedRegulatoryStatusInline,
        RegulatoryTimelineInline,
    ]
    
    def status_display_colored(self, obj):
        colors = {
            'functional': 'green',
            'implemented': 'green',
            'draft': 'orange',
            'development': 'blue',
            'under_review': 'purple',
            'none': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display_colored.short_description = 'Status'


@admin.register(MultilateralAgreement)
class MultilateralAgreementAdmin(admin.ModelAdmin):
    list_display = ['agreement_type', 'name', 'framework', 'signed_date', 'ratified_date']
    list_filter = ['agreement_type', 'framework__country']
    search_fields = ['name', 'framework__country__name']


@admin.register(RegulatoryInstitution)
class RegulatoryInstitutionAdmin(admin.ModelAdmin):
    list_display = ['institution', 'role', 'framework', 'order', 'is_active']
    list_filter = ['role', 'framework__country']
    search_fields = ['institution__name', 'mandate']


@admin.register(RegulatoryInstrument)
class RegulatoryInstrumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'instrument_type', 'date_enacted', 'coverage', 'is_current']
    list_filter = ['instrument_type', 'coverage', 'framework__country']
    search_fields = ['title', 'summary']


@admin.register(GedRegulatoryStatus)
class GedRegulatoryStatusAdmin(admin.ModelAdmin):
    list_display = ['framework', 'category', 'status', 'last_updated']
    list_filter = ['category', 'status', 'framework__country']
    search_fields = ['description']


@admin.register(RegulatoryTimeline)
class RegulatoryTimelineAdmin(admin.ModelAdmin):
    list_display = ['framework', 'event_type', 'title', 'event_date']
    list_filter = ['event_type', 'framework__country']
    search_fields = ['title', 'description']
    ordering = ['-event_date']


# ============ INFRASTRUCTURE & EQUIPMENT ADMIN ============

class EquipmentInline(admin.TabularInline):
    model = Equipment
    extra = 1
    fields = ['name', 'equipment_type', 'status', 'condition', 'is_active']


@admin.register(InfrastructureCategory)
class InfrastructureCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'order', 'is_active']
    list_filter = ['category_type', 'is_active']
    search_fields = ['name', 'description']


@admin.register(LaboratoryFacility)
class LaboratoryFacilityAdmin(admin.ModelAdmin):
    list_display = ['name', 'institution', 'biosafety_level', 'status', 'researcher_count']
    list_filter = ['status', 'biosafety_level', 'category']
    search_fields = ['name', 'institution__name', 'facility_type']
    readonly_fields = ['last_updated', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('institution', 'category', 'name', 'facility_type', 'biosafety_level', 'status')
        }),
        ('Description', {
            'fields': ('description', 'limitations', 'support_needed')
        }),
        ('Equipment & Capacity', {
            'fields': ('equipment_list', 'equipment_needs', 'capacity_description', 'researcher_count')
        }),
        ('Contact', {
            'fields': ('contact_person', 'contact_email', 'contact_phone')
        }),
        ('Metadata', {
            'fields': ('established_year', 'last_updated', 'is_active'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [EquipmentInline]


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'equipment_type', 'facility', 'status', 'condition']
    list_filter = ['equipment_type', 'status', 'condition', 'is_active']
    search_fields = ['name', 'model', 'manufacturer', 'serial_number']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'equipment_type', 'model', 'manufacturer', 'serial_number', 'facility')
        }),
        ('Status & Condition', {
            'fields': ('status', 'condition')
        }),
        ('Specifications', {
            'fields': ('specifications', 'acquisition_date', 'last_maintenance_date', 'next_maintenance_date')
        }),
        ('Usage', {
            'fields': ('is_shared', 'operational_hours', 'contact_person')
        }),
        ('Metadata', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(InfrastructureProject)
class InfrastructureProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'country', 'institution', 'status', 'priority', 'start_date']
    list_filter = ['status', 'priority', 'country']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TrainingCapacity)
class TrainingCapacityAdmin(admin.ModelAdmin):
    list_display = ['title', 'institution', 'training_type', 'skill_level', 'start_date']
    list_filter = ['training_type', 'skill_level', 'is_active']
    search_fields = ['title', 'description']


@admin.register(InfrastructureAssessment)
class InfrastructureAssessmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'country', 'assessment_area', 'assessment_date', 'score']
    list_filter = ['assessment_area', 'priority', 'country']
    search_fields = ['title', 'description']
