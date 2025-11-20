"""
Smart Reassignment Service for Support Management
"""
from django.utils import timezone
from datetime import timedelta
from tickets.models import Ticket
from orders.models import Dispute
from support_management.models import SupportProfile, SupportWorkloadTracker
from support_management.utils import send_support_notification


class SmartReassignmentService:
    """
    Service for intelligently reassigning tickets and disputes.
    """
    
    @staticmethod
    def reassign_ticket(ticket, target_agent=None):
        """
        Reassign a ticket to the best available agent or specific agent.
        
        Args:
            ticket: Ticket to reassign
            target_agent: Specific agent to assign to (optional)
        
        Returns:
            bool: True if reassigned successfully
        """
        if target_agent:
            ticket.assigned_to = target_agent
            ticket.save()
            send_support_notification(
                target_agent.support_profile,
                f"New ticket assigned: {ticket.subject}",
                priority="medium"
            )
            return True
        
        # Find best available agent
        best_agent = SmartReassignmentService._find_best_agent()
        
        if best_agent:
            ticket.assigned_to = best_agent
            ticket.save()
            send_support_notification(
                best_agent.support_profile,
                f"New ticket assigned: {ticket.subject}",
                priority="medium"
            )
            return True
        
        return False
    
    @staticmethod
    def reassign_dispute(dispute, target_agent=None):
        """
        Reassign a dispute to the best available agent or specific agent.
        
        Args:
            dispute: Dispute to reassign
            target_agent: Specific agent to assign to (optional)
        
        Returns:
            bool: True if reassigned successfully
        """
        if target_agent:
            dispute.assigned_to = target_agent
            dispute.save()
            send_support_notification(
                target_agent.support_profile,
                f"New dispute assigned: Order {dispute.order.id if dispute.order else 'N/A'}",
                priority="high"
            )
            return True
        
        # Find best available agent
        best_agent = SmartReassignmentService._find_best_agent()
        
        if best_agent:
            dispute.assigned_to = best_agent
            dispute.save()
            send_support_notification(
                best_agent.support_profile,
                f"New dispute assigned: Order {dispute.order.id if dispute.order else 'N/A'}",
                priority="high"
            )
            return True
        
        return False
    
    @staticmethod
    def _find_best_agent():
        """
        Find the best available agent based on workload.
        
        Returns:
            User: Best available support agent
        """
        # Get active support agents
        active_profiles = SupportProfile.objects.filter(status='active')
        
        if not active_profiles.exists():
            return None
        
        best_agent = None
        min_workload = float('inf')
        
        for profile in active_profiles:
            try:
                workload = SupportWorkloadTracker.objects.get(support_staff=profile.user)
                
                # Calculate current workload
                current_tickets = Ticket.objects.filter(
                    assigned_to=profile.user,
                    status__in=['open', 'in_progress']
                ).count()
                
                current_disputes = Dispute.objects.filter(
                    assigned_to=profile.user,
                    status='open'
                ).count()
                
                total_workload = current_tickets + current_disputes
                
                if total_workload < min_workload:
                    min_workload = total_workload
                    best_agent = profile.user
            except SupportWorkloadTracker.DoesNotExist:
                # If no workload tracker, assume low workload
                if min_workload == float('inf'):
                    best_agent = profile.user
                    min_workload = 0
        
        return best_agent
    
    @staticmethod
    def auto_reassign_inactive_agent_tasks():
        """
        Reassign all tasks from inactive agents.
        
        Returns:
            dict: Reassignment statistics
        """
        inactive_threshold = timezone.now() - timedelta(hours=6)
        
        # Get inactive agents
        inactive_agents = []
        for profile in SupportProfile.objects.filter(status='active'):
            try:
                workload = SupportWorkloadTracker.objects.get(support_staff=profile.user)
                if workload.last_activity and workload.last_activity < inactive_threshold:
                    inactive_agents.append(profile.user)
            except SupportWorkloadTracker.DoesNotExist:
                continue
        
        reassigned_tickets = 0
        reassigned_disputes = 0
        
        for agent in inactive_agents:
            # Reassign unassigned tickets
            tickets = Ticket.objects.filter(
                assigned_to=agent,
                status__in=['open', 'in_progress']
            )
            
            for ticket in tickets:
                if SmartReassignmentService.reassign_ticket(ticket):
                    reassigned_tickets += 1
            
            # Reassign open disputes
            disputes = Dispute.objects.filter(
                assigned_to=agent,
                status='open'
            )
            
            for dispute in disputes:
                if SmartReassignmentService.reassign_dispute(dispute):
                    reassigned_disputes += 1
        
        return {
            'reassigned_tickets': reassigned_tickets,
            'reassigned_disputes': reassigned_disputes,
            'inactive_agents': len(inactive_agents),
        }

