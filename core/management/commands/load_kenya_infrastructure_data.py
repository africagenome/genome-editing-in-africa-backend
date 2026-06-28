# infrastructure/management/commands/load_kenya_infrastructure_data.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date
from core.models import *


class Command(BaseCommand):
    help = 'Load Kenya infrastructure and equipment data'

    def handle(self, *args, **options):
        self.stdout.write('Loading Kenya infrastructure data...')
        
        # Get Kenya
        kenya = Country.objects.get(code='KEN')
        
        # Create Infrastructure Categories
        categories = {}
        category_data = [
            {'name': 'Universities', 'category_type': 'university', 'icon': 'fa-university'},
            {'name': 'Research Institutions', 'category_type': 'research_institution', 'icon': 'fa-flask'},
            {'name': 'CGIAR Centers', 'category_type': 'cg_center', 'icon': 'fa-globe'},
            {'name': 'Regulatory Bodies', 'category_type': 'regulatory_body', 'icon': 'fa-gavel'},
        ]
        
        for cat_data in category_data:
            cat, created = InfrastructureCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            categories[cat_data['name']] = cat
            if created:
                self.stdout.write(f'  Created category: {cat.name}')
        
        # University Data
        university_data = [
            {
                'name': 'Kenyatta University',
                'facility_type': 'Molecular lab with PCR machines, glasshouses',
                'biosafety_level': 'bsl2',
                'status': 'partially_equipped',
                'limitations': 'Political issue (non-enabling national procurement law), inadequate funding, unstable supply of power, maintenance challenge',
                'support_needed': 'Specialized procurement/waiver/exemptions',
                'researcher_count': 25,
            },
            {
                'name': 'University of Nairobi (CEBIB)',
                'facility_type': 'Molecular lab, tissue culture, Bioinformatics',
                'biosafety_level': 'bsl2',
                'status': 'partially_equipped',
                'limitations': 'Political issue (non-enabling national procurement law), inadequate funding, unstable supply of power, maintenance challenge',
                'support_needed': 'Specialized procurement/waiver/exemptions',
                'researcher_count': 30,
            },
            {
                'name': 'Egerton University',
                'facility_type': 'Molecular lab, tissue culture',
                'biosafety_level': 'none',
                'status': 'partially_equipped',
                'limitations': 'Political issue (non-enabling national procurement law), inadequate funding, unstable supply of power, maintenance challenge',
                'support_needed': 'Specialized procurement/waiver/exemptions',
                'researcher_count': 15,
            },
            {
                'name': 'Pwani University',
                'facility_type': 'Molecular lab, tissue culture, glasshouses, Bioinformatics',
                'biosafety_level': 'none',
                'status': 'partially_equipped',
                'limitations': 'Political issue (non-enabling national procurement law), inadequate funding, unstable supply of power, maintenance challenge',
                'support_needed': 'Specialized procurement/waiver/exemptions',
                'researcher_count': 18,
            },
            {
                'name': 'Jomo Kenyatta University of Agriculture and Technology',
                'facility_type': 'Molecular lab, tissue culture, glasshouses',
                'biosafety_level': 'none',
                'status': 'partially_equipped',
                'limitations': 'Political issue (non-enabling national procurement law), inadequate funding, unstable supply of power, maintenance challenge',
                'support_needed': 'Specialized procurement/waiver/exemptions',
                'researcher_count': 22,
            },
            {
                'name': 'University of Embu',
                'facility_type': 'Molecular lab, tissue culture, glasshouses',
                'biosafety_level': 'none',
                'status': 'partially_equipped',
                'limitations': 'Political issue (non-enabling national procurement law), inadequate funding, unstable supply of power, maintenance challenge',
                'support_needed': 'Specialized procurement/waiver/exemptions',
                'researcher_count': 12,
            },
            {
                'name': 'University of Eldoret',
                'facility_type': 'Molecular lab, tissue culture, glasshouses',
                'biosafety_level': 'none',
                'status': 'partially_equipped',
                'limitations': 'Political issue (non-enabling national procurement law), inadequate funding, unstable supply of power, maintenance challenge',
                'support_needed': 'Specialized procurement/waiver/exemptions',
                'researcher_count': 14,
            },
            {
                'name': 'Jaramogi Oginga Odinga University of Science and Technology',
                'facility_type': 'Molecular lab, tissue culture, glasshouse',
                'biosafety_level': 'none',
                'status': 'partially_equipped',
                'limitations': 'Political issue (non-enabling national procurement law), inadequate funding, unstable supply of power, maintenance challenge',
                'support_needed': 'Specialized procurement/waiver/exemptions',
                'researcher_count': 16,
            },
            {
                'name': 'Southeastern Kenya University',
                'facility_type': 'Molecular lab, tissue culture, glasshouse',
                'biosafety_level': 'none',
                'status': 'partially_equipped',
                'limitations': 'Political issue (non-enabling national procurement law), inadequate funding, unstable supply of power, maintenance challenge',
                'support_needed': 'Specialized procurement/waiver/exemptions',
                'researcher_count': 10,
            },
        ]
        
        university_category = categories['Universities']
        
        for uni_data in university_data:
            institution, created = Institution.objects.get_or_create(
                name=uni_data['name'],
                country=kenya,
                defaults={
                    'type': 'academic',
                }
            )
            
            facility, created = LaboratoryFacility.objects.get_or_create(
                institution=institution,
                name=uni_data['name'],
                defaults={
                    'category': university_category,
                    'facility_type': uni_data['facility_type'],
                    'biosafety_level': uni_data['biosafety_level'],
                    'status': uni_data['status'],
                    'limitations': uni_data['limitations'],
                    'support_needed': uni_data['support_needed'],
                    'researcher_count': uni_data['researcher_count'],
                    'description': f"{uni_data['name']} molecular laboratory facility with {uni_data['facility_type']}.",
                    'is_active': True,
                }
            )
            
            if created:
                self.stdout.write(f'  Created facility: {uni_data["name"]}')
        
        # Research Institutions Data
        research_data = [
            {
                'name': 'International Institute of Tropical Agriculture (IITA)',
                'facility_type': 'Molecular lab with PCR machines, glasshouses',
                'biosafety_level': 'bsl2',
                'status': 'fully_equipped',
                'limitations': 'Funding gap due to USAID exit',
                'support_needed': 'Specialized procurement/waiver/exemptions',
                'researcher_count': 40,
                'category': 'CGIAR Centers',
            },
            {
                'name': 'International Livestock Research Institute (ILRI)',
                'facility_type': 'Molecular lab with PCR machines, glasshouses',
                'biosafety_level': 'bsl2',
                'status': 'fully_equipped',
                'limitations': 'Funding gap due to USAID exit',
                'support_needed': 'Specialized procurement/waiver/exemptions',
                'researcher_count': 50,
                'category': 'CGIAR Centers',
            },
            {
                'name': 'International Centre of Insect Physiology and Ecology (ICIPE)',
                'facility_type': 'Molecular lab with PCR machines, glasshouses',
                'biosafety_level': 'bsl1',
                'status': 'fully_equipped',
                'limitations': 'Funding gap due to USAID exit',
                'support_needed': 'Specialized procurement/waiver/exemptions',
                'researcher_count': 35,
                'category': 'CGIAR Centers',
            },
            {
                'name': 'International Maize and Wheat Improvement Center (CIMMYT)',
                'facility_type': 'Molecular lab with PCR machines, glasshouses',
                'biosafety_level': 'none',
                'status': 'fully_equipped',
                'limitations': 'Funding gap due to USAID exit',
                'support_needed': 'Specialized procurement/waiver/exemptions',
                'researcher_count': 30,
                'category': 'CGIAR Centers',
            },
            {
                'name': 'Kenya Agricultural & Livestock Research Organization (KALRO)',
                'facility_type': 'Molecular lab with PCR machines, glasshouses',
                'biosafety_level': 'bsl1',
                'status': 'partially_equipped',
                'limitations': 'Inadequate funding',
                'support_needed': 'Specialized procurement/waiver/exemptions',
                'researcher_count': 45,
                'category': 'Research Institutions',
            },
            {
                'name': 'Kenya Forestry Research Institute (KEFRI)',
                'facility_type': 'Molecular lab with PCR machines, glasshouses',
                'biosafety_level': 'none',
                'status': 'partially_equipped',
                'limitations': 'Political issue (non-enabling national procurement law), inadequate funding, unstable supply of power, maintenance challenge',
                'support_needed': 'Specialized procurement/waiver/exemptions',
                'researcher_count': 20,
                'category': 'Research Institutions',
            },
        ]
        
        for res_data in research_data:
            institution, created = Institution.objects.get_or_create(
                name=res_data['name'],
                country=kenya,
                defaults={
                    'type': 'research',
                }
            )
            
            category = categories.get(res_data['category'], categories['Research Institutions'])
            
            facility, created = LaboratoryFacility.objects.get_or_create(
                institution=institution,
                name=res_data['name'],
                defaults={
                    'category': category,
                    'facility_type': res_data['facility_type'],
                    'biosafety_level': res_data['biosafety_level'],
                    'status': res_data['status'],
                    'limitations': res_data['limitations'],
                    'support_needed': res_data['support_needed'],
                    'researcher_count': res_data['researcher_count'],
                    'description': f"{res_data['name']} molecular laboratory facility with {res_data['facility_type']}.",
                    'is_active': True,
                }
            )
            
            if created:
                self.stdout.write(f'  Created facility: {res_data["name"]}')
        
        # Create Equipment entries for facilities
        equipment_data = [
            {
                'facility_name': 'International Institute of Tropical Agriculture (IITA)',
                'equipment': [
                    {'name': 'PCR Machine', 'type': 'pcr', 'status': 'operational', 'condition': 'excellent'},
                    {'name': 'DNA Sequencer', 'type': 'sequencer', 'status': 'operational', 'condition': 'good'},
                    {'name': 'Gel Electrophoresis System', 'type': 'gel_electrophoresis', 'status': 'operational', 'condition': 'good'},
                    {'name': 'Glasshouse Facility', 'type': 'glasshouse', 'status': 'operational', 'condition': 'excellent'},
                    {'name': 'Microscope', 'type': 'microscope', 'status': 'operational', 'condition': 'good'},
                ]
            },
            {
                'facility_name': 'International Livestock Research Institute (ILRI)',
                'equipment': [
                    {'name': 'PCR Machine', 'type': 'pcr', 'status': 'operational', 'condition': 'excellent'},
                    {'name': 'DNA Sequencer', 'type': 'sequencer', 'status': 'operational', 'condition': 'good'},
                    {'name': 'Centrifuge', 'type': 'centrifuge', 'status': 'operational', 'condition': 'excellent'},
                    {'name': 'Microscope', 'type': 'microscope', 'status': 'operational', 'condition': 'good'},
                    {'name': 'Bioanalyzer', 'type': 'bioanalyzer', 'status': 'operational', 'condition': 'good'},
                ]
            },
            {
                'facility_name': 'Kenyatta University',
                'equipment': [
                    {'name': 'PCR Machine', 'type': 'pcr', 'status': 'operational', 'condition': 'good'},
                    {'name': 'Gel Electrophoresis System', 'type': 'gel_electrophoresis', 'status': 'operational', 'condition': 'fair'},
                    {'name': 'Glasshouse', 'type': 'glasshouse', 'status': 'operational', 'condition': 'good'},
                ]
            },
            {
                'facility_name': 'University of Nairobi (CEBIB)',
                'equipment': [
                    {'name': 'PCR Machine', 'type': 'pcr', 'status': 'operational', 'condition': 'good'},
                    {'name': 'Bioinformatics System', 'type': 'bioinformatics', 'status': 'operational', 'condition': 'good'},
                    {'name': 'Tissue Culture Facility', 'type': 'tissue_culture', 'status': 'operational', 'condition': 'good'},
                ]
            },
        ]
        
        for eq_data in equipment_data:
            try:
                facility = LaboratoryFacility.objects.get(name=eq_data['facility_name'])
                for eq in eq_data['equipment']:
                    equipment, created = Equipment.objects.get_or_create(
                        facility=facility,
                        name=eq['name'],
                        defaults={
                            'equipment_type': eq['type'],
                            'status': eq['status'],
                            'condition': eq['condition'],
                            'is_active': True,
                        }
                    )
                    if created:
                        self.stdout.write(f'  Added equipment: {eq["name"]} to {eq_data["facility_name"]}')
            except LaboratoryFacility.DoesNotExist:
                self.stdout.write(f'  Facility not found: {eq_data["facility_name"]}')
        
        # Create Infrastructure Projects
        projects_data = [
            {
                'title': 'Capacity Building for Genome Editing Research in Kenya',
                'description': 'Enhance the capacity of Kenyan institutions to conduct genome editing research through infrastructure development and training.',
                'objectives': '1. Upgrade laboratory facilities at 5 universities\n2. Train 50 researchers in CRISPR technology\n3. Establish a national genome editing research network',
                'status': 'ongoing',
                'priority': 'high',
                'start_date': date(2023, 1, 1),
                'funding_amount': 2500000,
                'funding_source': 'AUDA-NEPAD',
                'equipment_needed': ['PCR Machines', 'DNA Sequencers', 'CRISPR Systems'],
                'contact_person': 'Dr. John Mwangi',
                'contact_email': 'jmwangi@auda-nepad.org',
            },
            {
                'title': 'Establishment of Biosafety Level 2 Laboratories in Kenyan Universities',
                'description': 'Establish BSL-2 laboratories at selected Kenyan universities to support genome editing research and training.',
                'objectives': '1. Construct BSL-2 labs at 4 universities\n2. Equip labs with modern equipment\n3. Train lab technicians',
                'status': 'planned',
                'priority': 'high',
                'start_date': date(2024, 6, 1),
                'funding_amount': 1500000,
                'funding_source': 'World Bank',
                'equipment_needed': ['Biosafety Cabinets', 'PCR Machines', 'Incubators'],
                'contact_person': 'Dr. Sarah Ochieng',
                'contact_email': 'sochieng@worldbank.org',
            },
            {
                'title': 'Kenya Genome Editing Equipment Modernization Program',
                'description': 'Modernize genome editing equipment at research institutions across Kenya.',
                'objectives': '1. Replace outdated equipment\n2. Install new sequencing platforms\n3. Establish maintenance contracts',
                'status': 'funding_required',
                'priority': 'medium',
                'start_date': date(2024, 9, 1),
                'funding_amount': 3000000,
                'funding_source': 'Private Sector',
                'equipment_needed': ['DNA Sequencers', 'Bioanalyzers', 'Liquid Handlers'],
                'contact_person': 'Dr. Peter Kariuki',
                'contact_email': 'pkariuki@kalro.go.ke',
            },
        ]
        
        for proj_data in projects_data:
            project, created = InfrastructureProject.objects.get_or_create(
                title=proj_data['title'],
                country=kenya,
                defaults=proj_data
            )
            if created:
                self.stdout.write(f'  Created infrastructure project: {project.title}')
        
        # Create Training Capacity entries
        training_data = [
            {
                'institution_name': 'University of Nairobi (CEBIB)',
                'title': 'CRISPR-Cas9 Genome Editing Workshop',
                'training_type': 'workshop',
                'description': 'Intensive workshop on CRISPR-Cas9 genome editing techniques for crop improvement and disease research.',
                'skill_level': 'intermediate',
                'max_participants': 25,
                'duration': '5 days',
                'topics_covered': ['CRISPR-Cas9', 'Gene Knockout', 'Gene Knock-in', 'Molecular Cloning'],
                'equipment_used': ['PCR Machines', 'Microscopes', 'Electroporator'],
                'is_featured': True,
            },
            {
                'institution_name': 'International Institute of Tropical Agriculture (IITA)',
                'title': 'Advanced Genome Editing for Cassava Improvement',
                'training_type': 'short_course',
                'description': 'Comprehensive training on genome editing techniques for cassava improvement, including virus resistance and yield enhancement.',
                'skill_level': 'advanced',
                'max_participants': 15,
                'duration': '2 weeks',
                'topics_covered': ['Cassava Genome', 'CRISPR-Cas9', 'Virus Resistance', 'Tissue Culture'],
                'equipment_used': ['DNA Sequencer', 'PCR Machines', 'Bioanalyzer'],
                'is_featured': True,
            },
            {
                'institution_name': 'Kenyatta University',
                'title': 'Basic Molecular Biology for Genome Editing',
                'training_type': 'short_course',
                'description': 'Foundation course in molecular biology techniques essential for genome editing research.',
                'skill_level': 'beginner',
                'max_participants': 30,
                'duration': '3 days',
                'topics_covered': ['DNA Extraction', 'PCR', 'Gel Electrophoresis', 'Molecular Cloning'],
                'equipment_used': ['PCR Machines', 'Gel Electrophoresis System', 'Centrifuge'],
            },
            {
                'institution_name': 'Kenya Agricultural & Livestock Research Organization (KALRO)',
                'title': 'Genome Editing for Livestock Improvement',
                'training_type': 'workshop',
                'description': 'Training on genome editing applications for livestock improvement, including disease resistance and productivity.',
                'skill_level': 'intermediate',
                'max_participants': 20,
                'duration': '5 days',
                'topics_covered': ['CRISPR-Cas9', 'Livestock Genomics', 'Gene Editing', 'Animal Health'],
                'equipment_used': ['PCR Machines', 'DNA Sequencer'],
            },
        ]
        
        for train_data in training_data:
            try:
                institution = Institution.objects.get(name=train_data['institution_name'])
                training, created = TrainingCapacity.objects.get_or_create(
                    institution=institution,
                    title=train_data['title'],
                    defaults=train_data
                )
                if created:
                    self.stdout.write(f'  Created training: {train_data["title"]}')
            except Institution.DoesNotExist:
                self.stdout.write(f'  Institution not found: {train_data["institution_name"]}')
        
        # Create Infrastructure Assessments
        assessment_data = [
            {
                'title': 'Kenyan University Laboratory Facilities Assessment',
                'assessment_area': 'laboratory',
                'description': 'Comprehensive assessment of laboratory facilities at Kenyan universities for genome editing research.',
                'current_status': 'Most universities have basic molecular biology laboratories but face constraints with consumables, sequencing services, and procurement processes.',
                'challenges': '1. Inadequate funding\n2. Unstable power supply\n3. Maintenance challenges\n4. Non-enabling procurement laws',
                'recommendations': '1. Specialized procurement waivers\n2. Increased funding allocation\n3. Infrastructure upgrades\n4. Maintenance training',
                'priority': 'high',
                'score': 45,
            },
            {
                'title': 'Research Institution Infrastructure Assessment',
                'assessment_area': 'laboratory',
                'description': 'Assessment of research institution facilities for genome editing research in Kenya.',
                'current_status': 'Research institutions and CGIAR centers have well-equipped laboratories but face funding limitations and bureaucratic procurement systems.',
                'challenges': '1. Funding gaps (USAID exit)\n2. Restricted access to specialized equipment\n3. High-throughput sequencing limitations',
                'recommendations': '1. Diversify funding sources\n2. Establish equipment sharing networks\n3. Improve procurement systems',
                'priority': 'high',
                'score': 65,
            },
            {
                'title': 'Genome Editing Equipment Needs Assessment',
                'assessment_area': 'equipment',
                'description': 'Assessment of equipment needs for genome editing research across Kenya.',
                'current_status': 'Kenyan institutions lack specialized equipment for advanced genome editing research.',
                'challenges': '1. Limited access to high-throughput sequencers\n2. Lack of CRISPR-specific equipment\n3. Maintenance challenges',
                'recommendations': '1. Centralized equipment facilities\n2. Equipment sharing programs\n3. Maintenance training programs',
                'priority': 'medium',
                'score': 35,
            },
        ]
        
        for ass_data in assessment_data:
            assessment, created = InfrastructureAssessment.objects.get_or_create(
                country=kenya,
                title=ass_data['title'],
                defaults={
                    'assessment_date': date(2024, 1, 15),
                    **ass_data
                }
            )
            if created:
                self.stdout.write(f'  Created assessment: {ass_data["title"]}')
        
        self.stdout.write(self.style.SUCCESS('✓ Kenya infrastructure data loaded successfully!'))
