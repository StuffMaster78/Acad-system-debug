## Academic Settings Population

This document explains how to populate academic settings (Paper Types, Formatting & Citation Styles, Subjects, Academic Levels, Types of Work, English Types, and Academic Level Pricing multipliers) for a website.

### What gets populated
- Paper Types: ~47 common academic paper types
- Formatting & Citation Styles: ~29 common styles (APA, MLA, Chicago, etc.)
- Academic Levels: 22 levels (High School to Post-Doctorate/Professional)
- Subjects: 130+ subjects across disciplines (technical flagged accordingly)
- Types of Work: Writing, Editing, Proofreading, etc.
- English Types: US, UK, AU, CA, International (with codes)
- Academic Level Pricing Multipliers

### Prerequisites
- Backend running with access to the database
- If Redis is not available locally, add `--skip-checks` to bypass system checks

### One-off script (direct)

Run against default/first website or provide a domain explicitly.

```bash
# Default (first website)
DB_HOST=localhost python3 populate_academic_settings.py

# Specific website
DB_HOST=localhost python3 populate_academic_settings.py example.com
```

### Management command (recommended)

```bash
# Default (first website)
python manage.py populate_academic_settings --skip-checks

# Specific website
python manage.py populate_academic_settings example.com --skip-checks
```

### Populate all websites

```bash
# Bash loop over every Website in the database
WEBSITES=$(python manage.py shell --skip-checks -c "from websites.models import Website; print('\n'.join([w.domain for w in Website.objects.all()]))")
for domain in $WEBSITES; do
  echo "Populating: $domain"
  python manage.py populate_academic_settings "$domain" --skip-checks
done
```

### Idempotency
The population is idempotent:
- Existing rows are preserved
- Missing rows are created
- Some items (e.g., subject technical flag, English code) are updated if needed

### Troubleshooting
- Redis not available: use `--skip-checks`
- Database host in local dev: export `DB_HOST=localhost`
- Inspect data in Django admin under Order Configs and Pricing Configs.


