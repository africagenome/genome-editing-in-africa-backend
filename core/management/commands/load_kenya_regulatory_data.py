# regulatory/management/commands/load_kenya_regulatory_data.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date
from core.models import *


class Command(BaseCommand):
    help = 'Load Kenya regulatory framework data'

    def handle(self, *args, **options):
        self.stdout.write('Loading Kenya regulatory framework data...')
        
        # Get or create Kenya
        kenya, created = Country.objects.get_or_create(
            code='KEN',
            defaults={
                'name': 'Kenya',
                'region_id': 1,  # East Africa
                'biosafety_status': 'functional',
                'readiness_score': 0.75,
                'active_projects': 13,
            }
        )
        
        # Create Regulatory Framework
        framework, created = RegulatoryFramework.objects.get_or_create(
            country=kenya,
            defaults={
                'status': 'functional',
                'approach': 'hybrid',
                'summary': """Kenya's regulatory framework for the governance of biotechnology and 
                genome-edited products comprises the Biosafety Act No. 2 of 2009, the Biosafety 
                (Contained Use) Regulations, 2011, the Biosafety (Environmental Release) Regulations, 
                2011, the Biosafety (Import, Export and Transit) Regulations, and the Guidelines for 
                Determining the Regulatory Process of Genome-Edited Organisms and Products in Kenya (2022).""",
                'biosafety_act_date': date(2009, 1, 1),
                'biosafety_regulations_date': date(2011, 1, 1),
                'ged_guidelines_date': date(2022, 1, 1),
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created Kenya regulatory framework'))
        else:
            self.stdout.write(self.style.WARNING('Kenya regulatory framework already exists'))
        
        # Add Multilateral Agreements
        agreements_data = [
            {
                'agreement_type': 'cac',
                'name': 'Codex Alimentarius Commission',
                'signed_date': date(1969, 1, 1),
                'ratified_date': date(1969, 1, 1),
                'reference_url': 'https://www.fao.org/fao-who-codexalimentarius/about-codex/members/en/',
            },
            {
                'agreement_type': 'unfccc',
                'name': 'UNFCCC Convention on Climate Change',
                'signed_date': date(1992, 1, 1),
                'ratified_date': date(1994, 1, 1),
                'reference_url': 'https://unfccc.int/resource/docs/natc/kennc2es.pdf',
            },
            {
                'agreement_type': 'cbd',
                'name': 'Convention on Biological Diversity',
                'signed_date': date(1992, 1, 1),
                'ratified_date': date(1993, 1, 1),
                'reference_url': 'https://www.cbd.int/doc/legal/cbd-en.pdf',
            },
            {
                'agreement_type': 'cpb',
                'name': 'Cartagena Protocol on Biosafety',
                'signed_date': date(2000, 1, 1),
                'ratified_date': date(2003, 1, 1),
                'reference_url': 'https://www.biosafetykenya.go.ke/images/COPMOB-Report.pdf',
            },
            {
                'agreement_type': 'nagoya',
                'name': 'Nagoya Protocol on Liability & Redress, Access & Benefit Sharing',
                'signed_date': date(2010, 1, 1),
                'ratified_date': date(2014, 1, 1),
                'reference_url': 'https://www.cbd.int/abs/nagoya-protocol/signatories',
            },
        ]
        
        for agreement_data in agreements_data:
            agreement, created = MultilateralAgreement.objects.get_or_create(
                framework=framework,
                agreement_type=agreement_data['agreement_type'],
                defaults=agreement_data
            )
            if created:
                self.stdout.write(f'  Added agreement: {agreement.get_agreement_type_display()}')
        
        # Add Regulatory Institutions
        institutions_data = [
            {
                'name': 'National Biosafety Authority',
                'role': 'principal',
                'mandate': 'Transfer, handling and use of GEd and Biotech Products',
                'website': 'www.biosafetykenya.go.ke',
            },
            {
                'name': 'Kenya Plant Health Inspectorate Service',
                'role': 'specialized',
                'mandate': 'Plant products and growth stimulants, plant varieties, seed quality & health',
                'website': 'www.kephis.go.ke',
            },
            {
                'name': 'Department of Veterinary Services',
                'role': 'specialized',
                'mandate': 'Livestock and veterinary products, animal diseases and pests',
                'website': 'www.kilimo.go.ke',
            },
            {
                'name': 'Kenya Bureau of Standards',
                'role': 'standards',
                'mandate': 'Conformity of products to national standards',
                'website': 'www.kebs.org',
            },
            {
                'name': 'Kenya Industrial Property Institute',
                'role': 'ip',
                'mandate': 'Protection of intellectual property rights',
                'website': 'www.kipi.go.ke',
            },
        ]
        
        for inst_data in institutions_data:
            institution, created = Institution.objects.get_or_create(
                name=inst_data['name'],
                country=kenya,
                defaults={
                    'type': 'regulatory',
                    'website': inst_data['website'],
                }
            )
            
            reg_inst, created = RegulatoryInstitution.objects.get_or_create(
                framework=framework,
                institution=institution,
                defaults={
                    'role': inst_data['role'],
                    'mandate': inst_data['mandate'],
                    'website': inst_data['website'],
                }
            )
            if created:
                self.stdout.write(f'  Added institution: {institution.name}')
        
        # Add Regulatory Instruments
        instruments_data = [
            {
                'title': 'Biosafety Act No.2 of 2009',
                'instrument_type': 'act',
                'date_enacted': date(2009, 1, 1),
                'coverage': 'all',
                'summary': 'Contained use, environmental release, import, export, transit, and placing on the market of GMOs',
                'reference_url': 'www.biosafetykenya.go.ke',
            },
            {
                'title': 'Biosafety Contained Use Regulation 2011',
                'instrument_type': 'regulation',
                'date_enacted': date(2011, 1, 1),
                'coverage': 'contained_use',
                'summary': 'Contained use of GMOs',
                'reference_url': 'www.biosafetykenya.go.ke',
            },
            {
                'title': 'Biosafety Environmental Release Regulations 2011',
                'instrument_type': 'regulation',
                'date_enacted': date(2011, 1, 1),
                'coverage': 'environmental_release',
                'summary': 'Environmental release and placing in the market of GMOs',
                'reference_url': 'www.biosafetykenya.go.ke',
            },
            {
                'title': 'Biosafety Import, Export and Transit Regulations 2011',
                'instrument_type': 'regulation',
                'date_enacted': date(2011, 1, 1),
                'coverage': 'import_export',
                'summary': 'Import, export, and transit of GMOs',
                'reference_url': 'www.biosafetykenya.go.ke',
            },
            {
                'title': 'Biosafety Labelling Regulations 2012',
                'instrument_type': 'regulation',
                'date_enacted': date(2012, 1, 1),
                'coverage': 'labelling',
                'summary': 'Labelling of GMOs on the shelves in the market',
                'reference_url': 'www.biosafetykenya.go.ke',
            },
            {
                'title': 'Guidelines for determining the regulatory process of genome edited organisms and products in Kenya',
                'instrument_type': 'guideline',
                'date_enacted': date(2022, 1, 1),
                'coverage': 'all',
                'summary': 'All genome-edited organisms (GEds or GEOs) and derived-products',
                'reference_url': 'www.biosafetykenya.go.ke',
            },
            {
                'title': 'Kenya Plant Health Inspectorate Service Act',
                'instrument_type': 'act',
                'date_enacted': date(2012, 1, 1),
                'coverage': 'all',
                'summary': 'Plant Health and Quality Assurance',
                'reference_url': 'www.kephis.go.ke',
            },
            {
                'title': 'Plant Protection (General) Regulations',
                'instrument_type': 'regulation',
                'date_enacted': date(2021, 1, 1),
                'coverage': 'all',
                'summary': 'Prevention of pest introductions and spread, management of pests and weeds',
                'reference_url': 'www.kephis.go.ke',
            },
            {
                'title': 'Plant Protection Act Cap 324',
                'instrument_type': 'act',
                'date_enacted': date(2022, 1, 1),
                'coverage': 'all',
                'summary': 'Regulate movement of plant and related items',
                'reference_url': 'www.kephis.go.ke',
            },
            {
                'title': 'Seeds and Plant Varieties Act Cap 326',
                'instrument_type': 'act',
                'date_enacted': date(2022, 1, 1),
                'coverage': 'all',
                'summary': 'Testing, certification, and regulation of seeds and plant varieties',
                'reference_url': 'www.kephis.go.ke',
            },
            {
                'title': 'Plant Breeders Rights and Regulations',
                'instrument_type': 'regulation',
                'date_enacted': date(2022, 1, 1),
                'coverage': 'all',
                'summary': 'Grant right to plant breeders, upholding variety protection',
                'reference_url': 'www.kephis.go.ke',
            },
            {
                'title': 'Animal Diseases Act Cap 364',
                'instrument_type': 'act',
                'date_enacted': date(1965, 1, 1),
                'date_amended': date(2022, 1, 1),
                'coverage': 'all',
                'summary': 'Prevent, control, and eradicate animal diseases',
                'reference_url': 'www.kilimo.go.ke',
            },
            {
                'title': 'The Industrial Property Act Cap 509',
                'instrument_type': 'act',
                'date_enacted': date(2001, 1, 1),
                'date_amended': date(2022, 1, 1),
                'coverage': 'ip',
                'summary': 'Promoting innovation and providing a legal framework for the protection and regulation of industrial property rights',
                'reference_url': 'www.kipi.go.ke',
            },
            {
                'title': 'Standard Act',
                'instrument_type': 'act',
                'date_enacted': date(2012, 1, 1),
                'coverage': 'all',
                'summary': 'Promote standardization and provide conformity assessment services',
                'reference_url': 'www.kebs.org',
            },
        ]
        
        for inst_data in instruments_data:
            instrument, created = RegulatoryInstrument.objects.get_or_create(
                framework=framework,
                title=inst_data['title'],
                defaults=inst_data
            )
            if created:
                self.stdout.write(f'  Added instrument: {instrument.title}')
        
        # Add GEd Regulatory Statuses
        ged_statuses_data = [
            {
                'category': 'plants',
                'status': 'case_by_case',
                'description': 'Plants are assessed on a case-by-case basis under the Guidelines for determining the regulatory process of genome edited organisms and products in Kenya (2022)',
            },
            {
                'category': 'animals',
                'status': 'case_by_case',
                'description': 'Animals are assessed on a case-by-case basis under the Guidelines for determining the regulatory process of genome edited organisms and products in Kenya (2022)',
            },
            {
                'category': 'microorganisms',
                'status': 'case_by_case',
                'description': 'Microorganisms are assessed on a case-by-case basis under the Guidelines for determining the regulatory process of genome edited organisms and products in Kenya (2022)',
            },
            {
                'category': 'health',
                'status': 'case_by_case',
                'description': 'Human health applications are assessed on a case-by-case basis',
            },
            {
                'category': 'environmental',
                'status': 'case_by_case',
                'description': 'Environmental applications are assessed on a case-by-case basis',
            },
        ]
        
        for status_data in ged_statuses_data:
            status, created = GedRegulatoryStatus.objects.get_or_create(
                framework=framework,
                category=status_data['category'],
                defaults=status_data
            )
            if created:
                self.stdout.write(f'  Added GEd status: {status.get_category_display()}')
        
        # Add Regulatory Timeline
        timeline_data = [
            {
                'event_type': 'act_enacted',
                'title': 'Biosafety Act No.2 of 2009 Enacted',
                'description': 'The Biosafety Act established the National Biosafety Authority as the principal competent authority for biotechnology regulation.',
                'event_date': date(2009, 1, 1),
            },
            {
                'event_type': 'regulation_enacted',
                'title': 'Biosafety Regulations Enacted',
                'description': 'The Biosafety (Contained Use) Regulations, Biosafety (Environmental Release) Regulations, and Biosafety (Import, Export and Transit) Regulations were enacted.',
                'event_date': date(2011, 1, 1),
            },
            {
                'event_type': 'international_agreement',
                'title': 'Ratified Cartagena Protocol on Biosafety',
                'description': 'Kenya ratified the Cartagena Protocol on Biosafety, committing to the safe transfer, handling, and use of GMOs.',
                'event_date': date(2003, 1, 1),
            },
            {
                'event_type': 'guideline_published',
                'title': 'Guidelines for Genome-Edited Organisms Published',
                'description': 'Kenya published Guidelines for Determining the Regulatory Process of Genome-Edited Organisms and Products, providing clarity on the regulatory pathway for GEd products.',
                'event_date': date(2022, 1, 1),
            },
            {
                'event_type': 'cft_approved',
                'title': 'First GEd CFT Approved',
                'description': 'Kenya approved its first confined field trial for a genome-edited crop, advancing the commercialization pathway.',
                'event_date': date(2023, 1, 1),
            },
        ]
        
        for timeline_data in timeline_data:
            timeline, created = RegulatoryTimeline.objects.get_or_create(
                framework=framework,
                title=timeline_data['title'],
                defaults=timeline_data
            )
            if created:
                self.stdout.write(f'  Added timeline event: {timeline.title}')
        
        self.stdout.write(self.style.SUCCESS('✓ Kenya regulatory framework data loaded successfully!'))
