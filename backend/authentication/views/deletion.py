from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from authentication.models.deletion_requests import AccountDeletionRequest
# from users.models import User 
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import action


class AccountUnlockAPIView(APIView):
    """Handles account unlocking actions"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        View to submit a deletion request for the user's account.
        If a pending deletion request already exists, notify the user.
        Otherwise, create a new deletion request.
        """
        # Check if a pending deletion request exists for the user
        if AccountDeletionRequest.objects.filter(user=request.user, 
                                          status=AccountDeletionRequest.PENDING).exists():
            return Response({"message": "You already have a pending deletion request."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Create a new deletion request
        deletion_request = AccountDeletionRequest.objects.create(user=request.user)
        return Response({"message": "Deletion request created.", 
                         "request_id": deletion_request.id},
                         status=status.HTTP_201_CREATED)

    def get(self, request, request_id, *args, **kwargs):
        """
        View to display the status of the user's deletion request.
        Shows details like status and timestamps for confirmation or rejection.
        """
        deletion_request = get_object_or_404(AccountDeletionRequest, id=request_id, 
                                              user=request.user)
        return Response({
            'request_id': deletion_request.id,
            'status': deletion_request.status,
            'created_at': deletion_request.created_at,
            'updated_at': deletion_request.updated_at
        }, status=status.HTTP_200_OK)


class AdminDeletionApprovalAPIView(APIView):
    """
    Admin views to approve/reject deletion requests and manage account status
    """

    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk, *args, **kwargs):
        """
        Admin approves the account deletion request and schedules a soft deletion.
        The user account is frozen and will be deleted in 3 months.
        """
        deletion_request = get_object_or_404(AccountDeletionRequest, id=pk, 
                                              status=AccountDeletionRequest.PENDING)

        # Update request status to approved
        deletion_request.status = AccountDeletionRequest.APPROVED
        deletion_request.save()

        # Freeze the user account (soft delete)
        user = deletion_request.user
        user.freeze_account()  # Assuming a `freeze_account()` method is defined

        return Response(
            {"message": "Account deletion request approved. Account is now frozen and "
            "will be deleted in 3 months."},
            status=status.HTTP_200_OK
        )


class AdminDeletionRejectAPIView(APIView):
    """
    Admin rejects the account deletion request.
    """

    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk, *args, **kwargs):
        """
        Admin rejects the account deletion request with an optional reason.
        """
        deletion_request = get_object_or_404(AccountDeletionRequest, id=pk, 
                                              status=AccountDeletionRequest.PENDING)
        reason = request.data.get("reason", "No reason provided")

        # Reject the deletion request
        deletion_request.status = AccountDeletionRequest.REJECTED
        deletion_request.reject(reason)  # Assuming a `reject` method is defined

        return Response({"message": "Account deletion request rejected."}, 
                        status=status.HTTP_200_OK)