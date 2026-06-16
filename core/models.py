from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify


class OrganismCategory(models.Model):
    """
    Categories for organisms: Plant, Animal, Micro-organism, etc.
    """
    CATEGORY_TYPES = [
        ('plant', 'Plant'),
        ('animal', 'Animal'),
        ('microorganism', 'Micro-organism'),
        ('fungus', 'Fungus'),
        ('algae', 'Algae'),
        ('insect', 'Insect'),
        ('fish', 'Fish'),
        ('bird', 'Bird'),
        ('mammal', 'Mammal'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class (e.g., 'fa-seedling', 'fa-paw', 'fa-bacteria')")
    color_code = models.CharField(max_length=7, blank=True, help_text="Hex color code for UI (e.g., '#5B7E96')")
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Organism Category'
        verbose_name_plural = 'Organism Categories'
    
    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"


class Organism(models.Model):
    """
    Organisms used in genome editing projects (plants, animals, microorganisms)
    """
    COMMON_NAME_CHOICES = [
        ('maize', 'Maize / Corn'),
        ('cassava', 'Cassava'),
        ('sorghum', 'Sorghum'),
        ('cowpea', 'Cowpea'),
        ('banana', 'Banana'),
        ('rice', 'Rice'),
        ('wheat', 'Wheat'),
        ('soybean', 'Soybean'),
        ('teff', 'Teff'),
        ('cotton', 'Cotton'),
        ('tomato', 'Tomato'),
        ('cattle', 'Cattle'),
        ('pig', 'Pig'),
        ('chicken', 'Chicken'),
        ('goat', 'Goat'),
        ('sheep', 'Sheep'),
        ('fish', 'Fish'),
        ('mosquito', 'Mosquito'),
        ('e_coli', 'E. coli'),
        ('yeast', 'Yeast'),
        ('other', 'Other'),
    ]
    
    SCIENTIFIC_NAME_CHOICES = [
        ('zea_mays', 'Zea mays'),
        ('manihot_esculenta', 'Manihot esculenta'),
        ('sorghum_bicolor', 'Sorghum bicolor'),
        ('vigna_unguiculata', 'Vigna unguiculata'),
        ('musa_acuminata', 'Musa acuminata'),
        ('oryza_sativa', 'Oryza sativa'),
        ('triticum_aestivum', 'Triticum aestivum'),
        ('glycine_max', 'Glycine max'),
        ('eragrostis_tef', 'Eragrostis tef'),
        ('gossypium_hirsutum', 'Gossypium hirsutum'),
        ('solanum_lycopersicum', 'Solanum lycopersicum'),
        ('bos_taurus', 'Bos taurus'),
        ('sus_scrofa', 'Sus scrofa'),
        ('gallus_gallus', 'Gallus gallus'),
        ('capra_hircus', 'Capra hircus'),
        ('ovis_aries', 'Ovis aries'),
        ('anopheles_gambiae', 'Anopheles gambiae'),
        ('escherichia_coli', 'Escherichia coli'),
        ('saccharomyces_cerevisiae', 'Saccharomyces cerevisiae'),
    ]
    
    # Basic Information
    common_name = models.CharField(max_length=100, unique=True)
    scientific_name = models.CharField(max_length=100, unique=True)
    custom_name = models.CharField(max_length=200, blank=True, help_text="Other names")
    category = models.ForeignKey(OrganismCategory, on_delete=models.CASCADE, related_name='organisms')
    
    # Genome Information
    genome_size_mb = models.FloatField(null=True, blank=True, help_text="Genome size in megabases")
    chromosome_count = models.IntegerField(null=True, blank=True)
    ploidy = models.CharField(max_length=50, blank=True, help_text="e.g., Diploid, Tetraploid")
    
    # Description
    description = models.TextField(blank=True)
    native_region = models.CharField(max_length=200, blank=True)
    economic_importance = models.TextField(blank=True)
    
    # Images
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class")
    image = models.ImageField(upload_to='organisms/', blank=True, null=True)
    
    # Traits and Applications
    common_traits = models.JSONField(default=list, blank=True, help_text="List of common edited traits")
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['common_name']
        unique_together = ['common_name', 'scientific_name']
    
    def __str__(self):
        if self.custom_name:
            return self.custom_name
        return f"{self.get_common_name_display()} ({self.get_scientific_name_display()})"
    
    @property
    def display_name(self):
        if self.custom_name:
            return self.custom_name
        return self.get_common_name_display()


class Region(models.Model):
    """African regions for country classification"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Region'
        verbose_name_plural = 'Regions'
    
    def __str__(self):
        return self.name


class Country(models.Model):
    """Country profile with genome editing metrics"""
    
    BIOSAFETY_STATUS = [
        ('functional', 'Functional Framework'),
        ('draft', 'Draft Guidelines (Genome Editing Specific)'),
        ('development', 'Policy Development'),
        ('none', 'No Specific Framework'),
    ]
    
    CLASSIFICATION_CHOICES = [
        ('product', 'Product-based'),
        ('process', 'Process-based'),
        ('hybrid', 'Hybrid Approach'),
        ('none', 'Not specified'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=3, unique=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='countries')
    flag_emoji = models.CharField(max_length=20, blank=True)
    capital = models.CharField(max_length=100, blank=True)
    population = models.BigIntegerField(null=True, blank=True)
    
    # Regulatory Status
    biosafety_status = models.CharField(max_length=20, choices=BIOSAFETY_STATUS, default='development')
    ged_guidelines = models.CharField(max_length=100, blank=True, help_text="Genome Editing Guidelines status")
    classification_approach = models.CharField(max_length=20, choices=CLASSIFICATION_CHOICES, default='none')
    international_alignment = models.CharField(max_length=100, blank=True, help_text="Cartagena, AU Model Law, etc.")
    readiness_score = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(1)])
    
    # Metrics
    active_projects = models.IntegerField(default=0)
    confined_field_trials = models.IntegerField(default=0)
    publications_count = models.IntegerField(default=0)
    researchers_trained = models.IntegerField(default=0)
    institutions_count = models.IntegerField(default=0)
    funding_received = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Additional info
    website = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'
    
    def __str__(self):
        return self.name


class Institution(models.Model):
    """Research institutions, regulatory bodies, universities, etc."""
    
    TYPE_CHOICES = [
        ('research', 'Research Institution'),
        ('regulatory', 'Regulatory Body'),
        ('academic', 'Academic Institution'),
        ('private', 'Private Sector'),
        ('cso', 'Civil Society Organization'),
        ('international', 'International Partner'),
        ('government', 'Government Ministry'),
    ]
    
    name = models.CharField(max_length=300)
    acronym = models.CharField(max_length=50, blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='institutions')
    website = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='institutions/', blank=True, null=True)
    established_year = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class Expert(models.Model):
    """Genome editing experts and researchers"""
    
    SECTOR_CHOICES = [
        ('research', 'Research / Academia'),
        ('regulatory', 'Regulatory Authority'),
        ('policy', 'Policy Maker'),
        ('private', 'Private Sector'),
        ('cso', 'Civil Society'),
        ('media', 'Media / Communications'),
    ]
    
    EXPERTISE_CHOICES = [
        ('crispr', 'CRISPR-Cas9'),
        ('talens', 'TALENs'),
        ('zfns', 'ZFNs'),
        ('sdn', 'SDN Technologies'),
        ('regulatory', 'Regulatory / Biosafety'),
        ('crop_improvement', 'Crop Improvement'),
        ('gene_therapy', 'Gene Therapy / Health'),
        ('bioinformatics', 'Bioinformatics'),
        ('policy_ethics', 'Policy & Ethics'),
        ('capacity_building', 'Capacity Building'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='expert_profile')
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200, blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='experts', null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='experts')
    sector = models.CharField(max_length=20, choices=SECTOR_CHOICES)
    expertise = models.JSONField(default=list, help_text="List of expertise areas")
    bio = models.TextField()
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    linkedin = models.URLField(blank=True)
    researchgate = models.URLField(blank=True)
    google_scholar = models.URLField(blank=True)
    orcid = models.CharField(max_length=50, blank=True)
    publications_count = models.IntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    profile_image = models.ImageField(upload_to='experts/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.country.name}"


class Project(models.Model):
    """Genome editing projects across Africa"""
    
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('rd', 'Research & Development'),
        ('cft', 'Confined Field Trial'),
        ('commercial', 'Commercial Release'),
        ('completed', 'Completed'),
        ('suspended', 'Suspended'),
    ]
    
    TECH_CHOICES = [
        ('crispr', 'CRISPR-Cas9'),
        ('talens', 'TALENs'),
        ('zfns', 'ZFNs'),
        ('sdn1', 'SDN-1'),
        ('sdn2', 'SDN-2'),
        ('sdn3', 'SDN-3'),
        ('base_editing', 'Base Editing'),
        ('prime_editing', 'Prime Editing'),
    ]
    
    SECTOR_CHOICES = [
        ('agriculture', 'Agriculture (Crops & Livestock)'),
        ('health', 'Public Health (Disease Vector Control)'),
        ('industrial', 'Industrial/Forestry'),
        ('environmental', 'Environmental'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=500)
    slug = models.SlugField(blank=True, max_length=500)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='projects')
    sector = models.CharField(max_length=20, choices=SECTOR_CHOICES, default='agriculture')
    
    # Organism Relationships (NEW)
    organisms = models.ManyToManyField(Organism, related_name='projects', blank=True)
    primary_organism = models.ForeignKey(
        Organism, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='primary_projects'
    )
    
    # Legacy fields (keep for backward compatibility)
    # crop_focus = models.CharField(max_length=200, blank=True, help_text="[DEPRECATED] Use organisms instead")
    target_traits = models.JSONField(default=list, blank=True, help_text="Drought tolerance, pest resistance, etc.")
    
    # Technical Details
    technology = models.CharField(max_length=20, choices=TECH_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='rd')
    description = models.TextField()
    objectives = models.TextField(blank=True)
    key_achievements = models.TextField(blank=True)
    
    # Institutions
    lead_institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='lead_projects')
    partners = models.ManyToManyField(Institution, related_name='partner_projects', blank=True)
    
    # Timeline
    start_year = models.IntegerField()
    end_year = models.IntegerField(null=True, blank=True)
    
    # Funding
    funding_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    funding_source = models.CharField(max_length=300, blank=True)
    principal_investigator = models.CharField(max_length=200, blank=True)
    
    # Additional
    tags = models.JSONField(default=list, blank=True)
    website = models.URLField(blank=True)
    
    # CFT-specific fields
    cft_location = models.CharField(max_length=200, blank=True)
    cft_approval_date = models.DateField(null=True, blank=True)
    cft_size = models.FloatField(null=True, blank=True, help_text="Size in hectares")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_year', 'title']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:500]
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    

class Publication(models.Model):
    """Scientific publications, reports, policy briefs"""
    
    TYPE_CHOICES = [
        ('article', 'Journal Article'),
        ('report', 'Technical Report'),
        ('policy', 'Policy Brief'),
        ('guideline', 'Guideline / Framework'),
        ('book', 'Book Chapter'),
        ('conference', 'Conference Paper'),
        ('thesis', 'Thesis / Dissertation'),
    ]
    
    TOPIC_CHOICES = [
        ('regulatory', 'Regulatory & Policy'),
        ('agriculture', 'Agriculture & Crops'),
        ('health', 'Human Health'),
        ('capacity', 'Capacity Building'),
        ('ethics', 'Ethics & Governance'),
        ('socioeconomic', 'Socio-economic'),
        ('biosafety', 'Biosafety & Risk Assessment'),
    ]
    
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('fr', 'French'),
        ('pt', 'Portuguese'),
        ('ar', 'Arabic'),
        ('sw', 'Swahili'),
    ]
    
    title = models.CharField(max_length=500)
    authors = models.CharField(max_length=500)
    year = models.IntegerField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    topic = models.CharField(max_length=20, choices=TOPIC_CHOICES)
    abstract = models.TextField()
    keywords = models.CharField(max_length=500, blank=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name='publications')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True, related_name='publications')
    tags = models.JSONField(default=list, blank=True)
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    
    # File and links
    file = models.FileField(upload_to='publications/', blank=True, null=True)
    external_url = models.URLField(blank=True)
    doi = models.CharField(max_length=100, blank=True)
    isbn = models.CharField(max_length=50, blank=True)
    
    # Metrics
    downloads = models.IntegerField(default=0)
    citations = models.IntegerField(default=0)
    
    # Publication details
    journal = models.CharField(max_length=300, blank=True)
    volume = models.CharField(max_length=50, blank=True)
    issue = models.CharField(max_length=50, blank=True)
    pages = models.CharField(max_length=50, blank=True)
    publisher = models.CharField(max_length=200, blank=True)
    
    is_featured = models.BooleanField(default=False)
    is_open_access = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-year', '-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.year})"


class Protocol(models.Model):
    """Laboratory protocols, SOPs, and technical guides"""
    
    TECH_CHOICES = [
        ('crispr', 'CRISPR-Cas9'),
        ('talens', 'TALENs'),
        ('sdn', 'SDN-1 / SDN-2'),
        ('base_editing', 'Base Editing'),
        ('transformation', 'Plant Transformation'),
        ('genotyping', 'Genotyping'),
    ]
    
    TYPE_CHOICES = [
        ('sop', 'Standard Operating Procedure'),
        ('guide', 'Step-by-Step Guide'),
        ('template', 'Template / Checklist'),
        ('video', 'Video Tutorial'),
        ('workshop', 'Workshop Material'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    title = models.CharField(max_length=500)
    technology = models.CharField(max_length=30, choices=TECH_CHOICES)
    crop_application = models.CharField(max_length=200, blank=True)
    protocol_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='intermediate')
    description = models.TextField()
    materials = models.TextField(blank=True, help_text="Required materials and reagents")
    steps = models.TextField(help_text="Step-by-step procedure")
    expected_results = models.TextField(blank=True)
    troubleshooting = models.TextField(blank=True)
    references = models.TextField(blank=True)
    
    author_institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='protocols')
    authors = models.CharField(max_length=300, blank=True)
    
    # Files
    file_pdf = models.FileField(upload_to='protocols/', blank=True, null=True)
    video_url = models.URLField(blank=True)
    
    # Metrics
    downloads = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    rating_count = models.IntegerField(default=0)
    
    tags = models.JSONField(default=list, blank=True)
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-downloads', 'title']
    
    def __str__(self):
        return self.title


class Consultation(models.Model):
    """Public consultations on genome editing policies"""
    
    STATUS_CHOICES = [
        ('open', 'Open for Comments'),
        ('closed', 'Closed'),
        ('upcoming', 'Upcoming'),
        ('drafting', 'Under Drafting'),
    ]
    
    title = models.CharField(max_length=300)
    slug = models.SlugField(blank=True, max_length=300)
    description = models.TextField()
    background = models.TextField(blank=True, help_text="Background information")
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True, related_name='consultations')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True, related_name='consultations')
    document = models.FileField(upload_to='consultations/', blank=True, null=True)
    external_link = models.URLField(blank=True)
    opening_date = models.DateField()
    closing_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    contact_email = models.EmailField(blank=True, help_text="Contact for inquiries")
    instructions = models.TextField(blank=True, help_text="How to submit comments")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-opening_date']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:300]
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title


class ConsultationSubmission(models.Model):
    """Submissions from stakeholders for consultations"""
    
    STAKEHOLDER_TYPES = [
        ('researcher', 'Researcher / Academic'),
        ('regulator', 'Regulatory Official'),
        ('policymaker', 'Policy Maker'),
        ('private', 'Private Sector'),
        ('cso', 'Civil Society'),
        ('farmer', 'Farmer Organization'),
        ('general', 'General Public'),
    ]
    
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='submissions')
    name = models.CharField(max_length=200)
    email = models.EmailField()
    organization = models.CharField(max_length=300, blank=True)
    stakeholder_type = models.CharField(max_length=20, choices=STAKEHOLDER_TYPES)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    comments = models.TextField()
    attachments = models.FileField(upload_to='submissions/', blank=True, null=True)
    is_public = models.BooleanField(default=False, help_text="Allow public viewing of submission")
    is_approved = models.BooleanField(default=False)
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.name} - {self.consultation.title}"


class News(models.Model):
    """News articles, announcements, and updates"""
    
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, max_length=300)
    summary = models.TextField()
    content = models.TextField()
    featured_image = models.ImageField(upload_to='news/', blank=True, null=True)
    published_date = models.DateField()
    author = models.CharField(max_length=200, blank=True)
    source = models.CharField(max_length=200, blank=True)
    source_url = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False)
    tags = models.JSONField(default=list, blank=True)
    countries = models.ManyToManyField(Country, blank=True, related_name='news')
    views = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-published_date']
        verbose_name = 'News'
        verbose_name_plural = 'News'
    
    def __str__(self):
        return self.title


class FAQ(models.Model):
    """Frequently Asked Questions"""
    
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('technical', 'Technical'),
        ('regulatory', 'Regulatory'),
        ('ethics', 'Ethics'),
        ('funding', 'Funding & Opportunities'),
    ]
    
    question = models.CharField(max_length=500)
    answer = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    order = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'question']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
    
    def __str__(self):
        return self.question


class GlossaryTerm(models.Model):
    """Glossary of genome editing terms"""
    
    term = models.CharField(max_length=200, unique=True)
    definition = models.TextField()
    abbreviation = models.CharField(max_length=50, blank=True)
    category = models.CharField(max_length=100, blank=True)
    related_terms = models.ManyToManyField('self', symmetrical=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['term']
    
    def __str__(self):
        return self.term


class FundingOpportunity(models.Model):
    """Funding and grant opportunities"""
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closing_soon', 'Closing Soon'),
        ('closed', 'Closed'),
        ('upcoming', 'Upcoming'),
    ]
    
    title = models.CharField(max_length=300)
    description = models.TextField()
    donor = models.CharField(max_length=200)
    amount_range = models.CharField(max_length=100, blank=True)
    deadline = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    eligibility = models.TextField(blank=True)
    application_link = models.URLField(blank=True)
    countries_eligible = models.ManyToManyField(Country, blank=True, related_name='funding_opportunities')
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['deadline', '-created_at']
        verbose_name_plural = 'Funding Opportunities'
    
    def __str__(self):
        return self.title


class Event(models.Model):
    """Workshops, conferences, training events"""
    
    TYPE_CHOICES = [
        ('workshop', 'Workshop'),
        ('conference', 'Conference'),
        ('training', 'Training Course'),
        ('webinar', 'Webinar'),
        ('seminar', 'Seminar'),
    ]
    
    title = models.CharField(max_length=300)
    slug = models.SlugField(blank=True, max_length=300)
    event_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    venue = models.CharField(max_length=300, blank=True)
    location = models.CharField(max_length=200, blank=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    is_virtual = models.BooleanField(default=False)
    virtual_link = models.URLField(blank=True)
    registration_link = models.URLField(blank=True)
    registration_deadline = models.DateField(null=True, blank=True)
    fee = models.CharField(max_length=100, blank=True)
    target_audience = models.TextField(blank=True)
    organizer = models.CharField(max_length=200, blank=True)
    contact_email = models.EmailField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_date']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:300]
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title