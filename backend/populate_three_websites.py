#!/usr/bin/env python3
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','writing_system.settings')
import django
django.setup()

from websites.models import Website
from order_configs.models import PaperType, FormattingandCitationStyle, Subject, AcademicLevel, TypeOfWork, EnglishType
from order_configs.management.commands.populate_academic_settings import Command

# Populate the three test websites
sites = ['https://site-a.local', 'https://site-b.local', 'https://site-c.local']

for domain in sites:
    w = Website.objects.filter(domain=domain).first()
    if not w:
        print(f"⚠️  Website {domain} not found, skipping...")
        continue
    
    print(f"\n{'='*70}")
    print(f"Populating: {w.name} ({domain})")
    print('='*70)
    
    # Use the management command
    cmd = Command()
    cmd.handle(domain, skip_checks=True)

print(f"\n{'='*70}")
print("COMPLETE - All 3 websites populated!")
print('='*70)

