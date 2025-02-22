from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    SupportProfile, SupportNotification, SupportOrderManagement, 
    SupportMessage, SupportMessageAccess, SupportGlobalAccess, 
    SupportPermission, DisputeResolutionLog, SupportActionLog, 
    EscalationLog, SupportAvailability, SupportActivityLog, 
    PaymentIssueLog, SupportOrderFileManagement, WriterPerformanceLog,
    SupportWorkloadTracker, OrderDisputeSLA, FAQCategory, FAQManagement, 
    SupportDashboard
)
from orders.models import Order, Dispute
from tickets.models import Ticket
from order_files.models import OrderFile

User = get_user_model()


### **1️⃣ Support Profile Serializer**
class SupportProfileSerializer(serializers.ModelSerializer):
    """Handles serialization of support agent profiles."""
    class Meta:
        model = SupportProfile
        fields = '__all__'


### **2️⃣ Support Notifications Serializer**
class SupportNotificationSerializer(serializers.ModelSerializer):
    """Handles notifications for support agents."""
    
    class Meta:
        model = SupportNotification
        fields = '__all__'


### **3️⃣ Support Order Management Serializer**
class SupportOrderManagementSerializer(serializers.ModelSerializer):
    """Allows support to manage order statuses & dispute resolutions."""
    
    class Meta:
        model = SupportOrderManagement
        fields = '__all__'


### **4️⃣ Support Messages Serializer**
class SupportMessageSerializer(serializers.ModelSerializer):
    """Allows support to send messages to clients, writers, editors, and admins."""
    
    class Meta:
        model = SupportMessage
        fields = '__all__'


### **5️⃣ Support Message Access Serializer**
class SupportMessageAccessSerializer(serializers.ModelSerializer):
    """Controls support's ability to view and moderate messages."""
    
    class Meta:
        model = SupportMessageAccess
        fields = '__all__'


### **6️⃣ Support Global Access Serializer**
class SupportGlobalAccessSerializer(serializers.ModelSerializer):
    """Ensures support has full access to all orders, clients, and writers."""
    
    class Meta:
        model = SupportGlobalAccess
        fields = '__all__'


### **7️⃣ Support Permissions Serializer**
class SupportPermissionSerializer(serializers.ModelSerializer):
    """Defines permissions for support roles."""
    
    class Meta:
        model = SupportPermission
        fields = '__all__'


### **8️⃣ Dispute Resolution Log Serializer**
class DisputeResolutionLogSerializer(serializers.ModelSerializer):
    """Tracks dispute resolutions handled by support agents."""
    
    class Meta:
        model = DisputeResolutionLog
        fields = '__all__'


### **9️⃣ Support Action Log Serializer**
class SupportActionLogSerializer(serializers.ModelSerializer):
    """Tracks actions performed by support agents."""
    
    class Meta:
        model = SupportActionLog
        fields = '__all__'


### **🔟 Escalation Log Serializer**
class EscalationLogSerializer(serializers.ModelSerializer):
    """Logs cases escalated by support agents."""
    
    class Meta:
        model = EscalationLog
        fields = '__all__'


### **1️⃣1️⃣ Support Availability Serializer**
class SupportAvailabilitySerializer(serializers.ModelSerializer):
    """Tracks support availability and online status."""
    
    class Meta:
        model = SupportAvailability
        fields = '__all__'


### **1️⃣2️⃣ Support Activity Log Serializer**
class SupportActivityLogSerializer(serializers.ModelSerializer):
    """Logs all actions performed by support staff for auditing."""
    
    class Meta:
        model = SupportActivityLog
        fields = '__all__'


### **1️⃣3️⃣ Payment Issue Log Serializer**
class PaymentIssueLogSerializer(serializers.ModelSerializer):
    """Tracks financial issues and escalations for payment disputes."""
    
    class Meta:
        model = PaymentIssueLog
        fields = '__all__'


### **1️⃣4️⃣ Support Order File Management Serializer**
class SupportOrderFileManagementSerializer(serializers.ModelSerializer):
    """Handles file uploads, deletions, and access control by support."""
    
    class Meta:
        model = SupportOrderFileManagement
        fields = '__all__'


### **1️⃣5️⃣ Writer Performance Log Serializer**
class WriterPerformanceLogSerializer(serializers.ModelSerializer):
    """Logs writer performance issues and complaints for review."""
    
    class Meta:
        model = WriterPerformanceLog
        fields = '__all__'


### **1️⃣6️⃣ Support Workload Tracker Serializer**
class SupportWorkloadTrackerSerializer(serializers.ModelSerializer):
    """Tracks the workload of each support agent."""
    
    class Meta:
        model = SupportWorkloadTracker
        fields = '__all__'


### **1️⃣7️⃣ Order Dispute SLA Serializer**
class OrderDisputeSLASerializer(serializers.ModelSerializer):
    """Ensures support agents meet SLA compliance for orders and disputes."""
    
    class Meta:
        model = OrderDisputeSLA
        fields = '__all__'


### **1️⃣8️⃣ FAQ Category Serializer**
class FAQCategorySerializer(serializers.ModelSerializer):
    """Defines categories for FAQs (Writer FAQs, Client FAQs)."""
    
    class Meta:
        model = FAQCategory
        fields = '__all__'


### **1️⃣9️⃣ FAQ Management Serializer**
class FAQManagementSerializer(serializers.ModelSerializer):
    """Allows support to create, update, and manage FAQs."""
    
    class Meta:
        model = FAQManagement
        fields = '__all__'


### **2️⃣0️⃣ Support Dashboard Serializer**
class SupportDashboardSerializer(serializers.ModelSerializer):
    """Provides an overview of support workload and flagged issues."""
    
    class Meta:
        model = SupportDashboard
        fields = '__all__'