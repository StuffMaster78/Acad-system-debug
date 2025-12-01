"""
Management command to ensure all user groups exist with proper permissions.
"""
from django.core.management.base import BaseCommand
from users.services.group_service import UserGroupService


class Command(BaseCommand):
    help = 'Ensure all role-based user groups exist with proper permissions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update permissions for existing groups',
        )

    def handle(self, *args, **options):
        self.stdout.write('Ensuring all user groups exist...')
        self.stdout.write('=' * 70)
        
        results = UserGroupService.ensure_all_groups_exist()
        
        created_count = sum(1 for _, created in results.values() if created)
        existing_count = len(results) - created_count
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Groups ensured: {created_count} created, {existing_count} already existed'
        ))
        
        for role, (group, created) in results.items():
            if group:
                status = self.style.SUCCESS('✓') if created else self.style.WARNING('-')
                self.stdout.write(
                    f'{status} {role:15} → {group.name:20} '
                    f'({len(group.permissions.all())} permissions)'
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'✗ {role:15} → Failed to create group')
                )

