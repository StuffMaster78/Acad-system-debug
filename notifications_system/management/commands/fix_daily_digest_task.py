"""
Management command to fix the send_daily_digest task name in PeriodicTask records.
Updates any PeriodicTask records that reference the old task name.
"""
from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask


class Command(BaseCommand):
    help = 'Fix the send_daily_digest task name in PeriodicTask records'

    def handle(self, *args, **options):
        # Find all PeriodicTask records with the old task name
        old_task_name = 'notifications_system.tasks.send_daily_digest'
        new_task_name = 'notifications_system.tasks.send_daily_digests'
        
        tasks = PeriodicTask.objects.filter(task=old_task_name)
        
        if not tasks.exists():
            self.stdout.write(
                self.style.SUCCESS(
                    f'No PeriodicTask records found with task name: {old_task_name}'
                )
            )
            return
        
        count = tasks.count()
        self.stdout.write(
            self.style.WARNING(
                f'Found {count} PeriodicTask record(s) with old task name. Updating...'
            )
        )
        
        # Update all matching records
        updated = tasks.update(task=new_task_name)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated {updated} PeriodicTask record(s) to use task name: {new_task_name}'
            )
        )
        
        # Also check for tasks with similar names that might be wrong
        similar_tasks = PeriodicTask.objects.filter(
            task__icontains='send_daily_digest'
        ).exclude(task=new_task_name)
        
        if similar_tasks.exists():
            self.stdout.write(
                self.style.WARNING(
                    f'\nFound {similar_tasks.count()} other task(s) with similar names:'
                )
            )
            for task in similar_tasks:
                self.stdout.write(f'  - {task.name}: {task.task}')

