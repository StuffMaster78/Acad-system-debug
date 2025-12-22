"""
Service for intelligent task reassignment based on SLA and workload.
"""
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from support_management.models import OrderDisputeSLA, SupportProfile, SupportWorkloadTracker
from orders.models import Order, Dispute
from tickets.models import Ticket
import logging

logger = logging.getLogger(__name__)


class SmartReassignmentService:
    """
    Service for intelligent reassignment of tasks based on SLA breaches and workload.
    """
    
    @staticmethod
    def auto_reassign_inactive_agent_tasks():
        """
        Automatically reassign tasks from inactive agents.
        Returns count of reassigned items.
        """
        # Get inactive agents
        inactive_profiles = SupportProfile.objects.filter(status='inactive')
        inactive_users = [p.user for p in inactive_profiles if p.user]
        
        if not inactive_users:
            return {'reassigned_tickets': 0, 'reassigned_disputes': 0}
        
        reassigned_tickets = 0
        reassigned_disputes = 0
        
        # Reassign tickets
        tickets = Ticket.objects.filter(
            assigned_to__in=inactive_users,
            status__in=['open', 'in_progress']
        )
        
        for ticket in tickets:
            new_agent = SmartReassignmentService.find_best_available_agent(
                exclude_user=ticket.assigned_to
            )
            if new_agent:
                ticket.assigned_to = new_agent
                ticket.save(update_fields=['assigned_to'])
                reassigned_tickets += 1
        
        # Reassign disputes
        disputes = Dispute.objects.filter(
            assigned_to__in=inactive_users,
            status__in=['open', 'in_progress']
        )
        
        for dispute in disputes:
            new_agent = SmartReassignmentService.find_best_available_agent(
                exclude_user=dispute.assigned_to
            )
            if new_agent:
                dispute.assigned_to = new_agent
                dispute.save(update_fields=['assigned_to'])
                reassigned_disputes += 1
        
        return {
            'reassigned_tickets': reassigned_tickets,
            'reassigned_disputes': reassigned_disputes
        }
    
    @staticmethod
    def auto_reassign_breached_slas():
        """
        Automatically reassign breached SLAs to available agents.
        Only reassigns if breach duration > 1 hour.
        """
        breached_slas = OrderDisputeSLA.objects.filter(
            sla_breached=True,
            actual_resolution_time__isnull=True,
            breach_duration_minutes__gte=60  # Only reassign if breached for > 1 hour
        ).select_related('assigned_to', 'order', 'dispute')
        
        reassigned_count = 0
        
        for sla in breached_slas:
            # Find best available agent
            new_agent = SmartReassignmentService.find_best_available_agent(
                exclude_user=sla.assigned_to,
                sla_type=sla.sla_type
            )
            
            if new_agent:
                old_agent = sla.assigned_to
                sla.assigned_to = new_agent
                sla.save(update_fields=['assigned_to'])
                
                logger.info(
                    f"Reassigned SLA {sla.id} from {old_agent.username if old_agent else 'Unassigned'} "
                    f"to {new_agent.username} due to breach"
                )
                reassigned_count += 1
        
        return {
            'reassigned_slas': reassigned_count,
            'total_breached': breached_slas.count()
        }
    
    @staticmethod
    def find_best_available_agent(exclude_user=None, sla_type=None):
        """
        Find the best available support agent for reassignment.
        Considers:
        - Active status
        - Current workload
        - SLA compliance rate
        - Availability
        """
        # Get active support profiles
        active_profiles = SupportProfile.objects.filter(
            status='active'
        ).exclude(user=exclude_user) if exclude_user else SupportProfile.objects.filter(status='active')
        
        if not active_profiles.exists():
            return None
        
        # Get workload for each agent
        best_agent = None
        best_score = float('inf')  # Lower is better
        
        for profile in active_profiles:
            if not profile.user:
                continue
            
            # Calculate workload score
            workload_tracker, _ = SupportWorkloadTracker.objects.get_or_create(
                support_staff=profile.user
            )
            
            # Count active SLAs
            active_slas = OrderDisputeSLA.objects.filter(
                assigned_to=profile.user,
                actual_resolution_time__isnull=True
            ).count()
            
            # Count breached SLAs (penalty)
            breached_slas = OrderDisputeSLA.objects.filter(
                assigned_to=profile.user,
                sla_breached=True,
                actual_resolution_time__isnull=True
            ).count()
            
            # Calculate score (lower is better)
            # Base workload + breached SLAs penalty
            score = active_slas + (breached_slas * 3)  # Breached SLAs count 3x
            
            # Add ticket/dispute workload
            score += workload_tracker.tickets_handled or 0
            score += workload_tracker.disputes_handled or 0
            
            if score < best_score:
                best_score = score
                best_agent = profile.user
        
        return best_agent
    
    @staticmethod
    def balance_workload():
        """
        Balance workload across all active support agents.
        Reassigns tasks from overloaded agents to underloaded agents.
        """
        active_profiles = SupportProfile.objects.filter(status='active')
        
        if active_profiles.count() < 2:
            return {'reassigned': 0, 'message': 'Need at least 2 active agents for balancing'}
        
        # Calculate workload for each agent
        agent_workloads = []
        for profile in active_profiles:
            if not profile.user:
                continue
            
            active_slas = OrderDisputeSLA.objects.filter(
                assigned_to=profile.user,
                actual_resolution_time__isnull=True
            ).count()
            
            agent_workloads.append({
                'user': profile.user,
                'workload': active_slas
            })
        
        if not agent_workloads:
            return {'reassigned': 0, 'message': 'No active agents with workload'}
        
        # Sort by workload
        agent_workloads.sort(key=lambda x: x['workload'])
        
        # Calculate average workload
        total_workload = sum(a['workload'] for a in agent_workloads)
        avg_workload = total_workload / len(agent_workloads) if agent_workloads else 0
        
        # Reassign from overloaded to underloaded
        reassigned_count = 0
        
        # Get overloaded agents (workload > avg * 1.5)
        overloaded = [a for a in agent_workloads if a['workload'] > avg_workload * 1.5]
        # Get underloaded agents (workload < avg * 0.5)
        underloaded = [a for a in agent_workloads if a['workload'] < avg_workload * 0.5]
        
        for overloaded_agent in overloaded:
            if not underloaded:
                break
            
            # Get SLAs from overloaded agent (non-breached, non-warning first)
            slas_to_reassign = OrderDisputeSLA.objects.filter(
                assigned_to=overloaded_agent['user'],
                actual_resolution_time__isnull=True
            ).exclude(status='breached').order_by('expected_resolution_time')
            
            # Reassign up to the difference
            target_reassign = int(overloaded_agent['workload'] - avg_workload)
            
            for sla in slas_to_reassign[:target_reassign]:
                # Find best underloaded agent
                best_underloaded = min(underloaded, key=lambda x: x['workload'])
                
                old_agent = sla.assigned_to
                sla.assigned_to = best_underloaded['user']
                sla.save(update_fields=['assigned_to'])
                
                # Update workload counts
                best_underloaded['workload'] += 1
                overloaded_agent['workload'] -= 1
                reassigned_count += 1
                
                logger.info(
                    f"Balanced workload: Reassigned SLA {sla.id} from {old_agent.username} "
                    f"to {best_underloaded['user'].username}"
                )
        
        return {
            'reassigned': reassigned_count,
            'message': f'Reassigned {reassigned_count} SLAs for workload balancing'
        }
