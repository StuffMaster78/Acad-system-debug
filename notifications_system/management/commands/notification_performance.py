"""
Management command to analyze notification system performance.
"""
from django.core.management.base import BaseCommand
from notifications_system.monitoring.performance import get_performance_monitor
from notifications_system.services.smart_resolver import get_smart_resolver
import json


class Command(BaseCommand):
    help = 'Analyze notification system performance metrics'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            choices=['json', 'table'],
            default='table',
            help='Output format'
        )
        parser.add_argument(
            '--metric',
            type=str,
            help='Specific metric to analyze'
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all metrics after analysis'
        )
    
    def handle(self, *args, **options):
        """Handle the command."""
        monitor = get_performance_monitor()
        resolver = get_smart_resolver()
        
        # Get performance statistics
        stats = monitor.get_notification_stats()
        resolver_stats = resolver.get_performance_stats()
        
        if options['format'] == 'json':
            self._output_json(stats, resolver_stats)
        else:
            self._output_table(stats, resolver_stats)
        
        if options['reset']:
            monitor.monitor.reset_metrics()
            self.stdout.write(
                self.style.SUCCESS('Metrics reset successfully')
            )
    
    def _output_json(self, stats, resolver_stats):
        """Output statistics in JSON format."""
        output = {
            'performance_metrics': stats,
            'template_resolver_stats': resolver_stats
        }
        
        self.stdout.write(json.dumps(output, indent=2))
    
    def _output_table(self, stats, resolver_stats):
        """Output statistics in table format."""
        self.stdout.write(self.style.SUCCESS('=== Notification Performance Metrics ==='))
        
        for metric_name, metric_stats in stats.items():
            if metric_stats['count'] > 0:
                self.stdout.write(f"\n{metric_name.upper()}:")
                self.stdout.write(f"  Count: {metric_stats['count']}")
                self.stdout.write(f"  Average: {metric_stats['avg']:.2f}ms")
                self.stdout.write(f"  Min: {metric_stats['min']:.2f}ms")
                self.stdout.write(f"  Max: {metric_stats['max']:.2f}ms")
                self.stdout.write(f"  95th percentile: {metric_stats['p95']:.2f}ms")
        
        self.stdout.write(self.style.SUCCESS('\n=== Template Resolver Performance ==='))
        
        for event_key, methods in resolver_stats.items():
            self.stdout.write(f"\n{event_key}:")
            for method, method_stats in methods.items():
                self.stdout.write(f"  {method}:")
                self.stdout.write(f"    Average: {method_stats['avg_duration']:.2f}ms")
                self.stdout.write(f"    Min: {method_stats['min_duration']:.2f}ms")
                self.stdout.write(f"    Max: {method_stats['max_duration']:.2f}ms")
                self.stdout.write(f"    Count: {method_stats['count']}")
