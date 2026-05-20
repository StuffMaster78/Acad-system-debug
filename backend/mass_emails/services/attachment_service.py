from __future__ import annotations

from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from files_management.enums import FilePurpose, FileVisibility
from files_management.services import FileAttachmentService, FileUploadService
from mass_emails.models import CampaignAttachment, EmailCampaign


class CampaignAttachmentService:
    """
    Upload and attach campaign files through files_management.

    Mass emails own the campaign workflow. The central files app owns
    storage, metadata, validation, and attachment records.
    """

    @staticmethod
    @transaction.atomic
    def upload_attachment(
        *,
        campaign: EmailCampaign,
        uploaded_by,
        uploaded_file: UploadedFile,
        name: str = "",
    ) -> CampaignAttachment:
        """
        Store a campaign attachment and link it to the campaign.
        """

        display_name = name or uploaded_file.name
        metadata = {
            "source_domain": "mass_emails",
            "campaign_id": campaign.id,
        }

        managed_file = FileUploadService.upload_file(
            website=campaign.website,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            purpose=FilePurpose.MASS_EMAIL_ATTACHMENT,
            is_public=False,
            metadata=metadata,
        )
        attachment = FileAttachmentService.attach_managed_file(
            website=campaign.website,
            obj=campaign,
            managed_file=managed_file,
            purpose=FilePurpose.MASS_EMAIL_ATTACHMENT,
            visibility=FileVisibility.STAFF_ONLY,
            attached_by=uploaded_by,
            display_name=display_name,
            metadata=metadata,
        )

        return CampaignAttachment.objects.create(
            campaign=campaign,
            attachment=attachment,
            name=display_name,
            created_by=uploaded_by,
        )
