# core/signals.py

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from .models import Project, Consultation, News, Event, Country


@receiver(pre_save, sender=Project)
def project_pre_save(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.title)[:500]


@receiver(pre_save, sender=Consultation)
def consultation_pre_save(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.title)[:300]


@receiver(pre_save, sender=News)
def news_pre_save(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.title)[:300]


@receiver(pre_save, sender=Event)
def event_pre_save(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.title)[:300]


@receiver(post_save, sender=Country)
def update_country_metrics(sender, instance, **kwargs):
    """Update country metrics when related data changes"""
    # Avoid recursion by checking if update is needed
    project_count = instance.projects.exclude(status='completed').count()
    cft_count = instance.projects.filter(status='cft').count()
    pub_count = instance.publications.count()
    inst_count = instance.institutions.count()
    
    if (instance.active_projects != project_count or 
        instance.confined_field_trials != cft_count or
        instance.publications_count != pub_count or
        instance.institutions_count != inst_count):
        instance.active_projects = project_count
        instance.confined_field_trials = cft_count
        instance.publications_count = pub_count
        instance.institutions_count = inst_count
        instance.save(update_fields=['active_projects', 'confined_field_trials', 
                                      'publications_count', 'institutions_count'])