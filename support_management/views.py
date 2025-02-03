from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import (
    SupportProfile, SupportNotification, SupportOrderManagement,
    SupportMessage, SupportGlobalAccess, SupportPermission,
    DisputeResolutionLog, SupportActionLog, EscalationLog, 
    SupportAvailability, SupportActivityLog, PaymentIssueLog,
    SupportOrderFileManagement, WriterPerformanceLog,
    SupportWorkloadTracker, OrderDisputeSLA, FAQCategory, FAQManagement,
    SupportDashboard
)
from .serializers import (
    SupportProfileSerializer, SupportNotificationSerializer, 
    SupportOrderManagementSerializer, SupportMessageSerializer, 
    SupportGlobalAccessSerializer, SupportPermissionSerializer, 
    DisputeResolutionLogSerializer, SupportActionLogSerializer, 
    EscalationLogSerializer, SupportAvailabilitySerializer, 
    SupportActivityLogSerializer, PaymentIssueLogSerializer,
    SupportOrderFileManagementSerializer, WriterPerformanceLogSerializer, 
    SupportWorkloadTrackerSerializer, OrderDisputeSLASerializer, 
    FAQCategorySerializer, FAQManagementSerializer, 
    SupportDashboardSerializer
)
from .permissions import (
    IsSupportAgent, IsAdminOrSuperAdmin, CanManageOrders, 
    CanHandleDisputes, CanRecommendBlacklist, CanModerateMessages, 
    CanManageWriterPerformance, CanEscalateIssues, CanAccessSupportDashboard
)

# 🚀 **1️⃣ Support Profile ViewSet**
class SupportProfileViewSet(viewsets.ModelViewSet):
    queryset = SupportProfile.objects.all()
    serializer_class = SupportProfileSerializer
    permission_classes = [IsAdminOrSuperAdmin]

    def get_queryset(self):
        """Admins can view all support profiles, support can view their own."""
        if self.request.user.role == "support":
            return SupportProfile.objects.filter(user=self.request.user)
        return super().get_queryset()


# 🚀 **2️⃣ Support Notifications ViewSet**
class SupportNotificationViewSet(viewsets.ModelViewSet):
    queryset = SupportNotification.objects.all()
    serializer_class = SupportNotificationSerializer
    permission_classes = [IsSupportAgent]

    def get_queryset(self):
        return SupportNotification.objects.filter(support_staff=self.request.user.support_profile)

    @action(detail=False, methods=["post"])
    def mark_as_read(self, request):
        """Marks all notifications as read for the current support agent."""
        notifications = self.get_queryset()
        notifications.update(is_read=True)
        return Response({"message": "Notifications marked as read."}, status=status.HTTP_200_OK)


# 🚀 **3️⃣ Support Order Management ViewSet**
class SupportOrderManagementViewSet(viewsets.ModelViewSet):
    queryset = SupportOrderManagement.objects.all()
    serializer_class = SupportOrderManagementSerializer
    permission_classes = [CanManageOrders]

    @action(detail=True, methods=["post"])
    def restore_to_progress(self, request, pk=None):
        """Restores an order back to progress."""
        instance = self.get_object()
        instance.restore_order_progress()
        return Response({"message": "Order restored to progress."}, status=status.HTTP_200_OK)


# 🚀 **4️⃣ Support Messages ViewSet**
class SupportMessageViewSet(viewsets.ModelViewSet):
    queryset = SupportMessage.objects.all()
    serializer_class = SupportMessageSerializer
    permission_classes = [CanModerateMessages]

    def get_queryset(self):
        """Support can see only their messages or those they moderate."""
        return SupportMessage.objects.filter(sender=self.request.user) | \
               SupportMessage.objects.filter(recipient=self.request.user)

    @action(detail=True, methods=["post"])
    def flag_message(self, request, pk=None):
        """Flags a message as inappropriate."""
        instance = self.get_object()
        instance.flag_message()
        return Response({"message": "Message flagged for review."}, status=status.HTTP_200_OK)


# 🚀 **5️⃣ Escalation Log ViewSet**
class EscalationLogViewSet(viewsets.ModelViewSet):
    queryset = EscalationLog.objects.all()
    serializer_class = EscalationLogSerializer
    permission_classes = [CanEscalateIssues]

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Approves an escalation request."""
        instance = self.get_object()
        if request.user.role in ["admin", "superadmin"]:
            instance.approve(admin=request.user)
            return Response({"message": "Escalation approved."}, status=status.HTTP_200_OK)
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)


# 🚀 **6️⃣ Support Workload Tracker ViewSet**
class SupportWorkloadTrackerViewSet(viewsets.ModelViewSet):
    queryset = SupportWorkloadTracker.objects.all()
    serializer_class = SupportWorkloadTrackerSerializer
    permission_classes = [IsAdminOrSuperAdmin]


# 🚀 **7️⃣ Payment Issue Log ViewSet**
class PaymentIssueLogViewSet(viewsets.ModelViewSet):
    queryset = PaymentIssueLog.objects.all()
    serializer_class = PaymentIssueLogSerializer
    permission_classes = [IsSupportAgent]

    @action(detail=True, methods=["post"])
    def escalate_issue(self, request, pk=None):
        """Escalates a payment issue to an admin."""
        instance = self.get_object()
        instance.escalate_issue(admin=request.user)
        return Response({"message": "Payment issue escalated."}, status=status.HTTP_200_OK)


# 🚀 **8️⃣ FAQ Management ViewSet**
class FAQManagementViewSet(viewsets.ModelViewSet):
    queryset = FAQManagement.objects.all()
    serializer_class = FAQManagementSerializer
    permission_classes = [IsSupportAgent]


# 🚀 **9️⃣ Support Dashboard ViewSet**
class SupportDashboardViewSet(viewsets.ModelViewSet):
    queryset = SupportDashboard.objects.all()
    serializer_class = SupportDashboardSerializer
    permission_classes = [CanAccessSupportDashboard]

    @action(detail=False, methods=["post"])
    def refresh_dashboard(self, request):
        """Refreshes all support dashboards."""
        SupportDashboard.refresh_all_dashboards()
        return Response({"message": "Support dashboards refreshed."}, status=status.HTTP_200_OK)
