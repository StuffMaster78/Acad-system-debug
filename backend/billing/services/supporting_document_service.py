from __future__ import annotations

from django.core.exceptions import ValidationError

from billing.models.supporting_document import SupportingDocument


class SupportingDocumentService:
    """
    Own creation and metadata updates for billing supporting documents.

    Supporting documents may be linked to invoices or payment requests.
    """

    @staticmethod
    def _validate_target(
        *,
        invoice=None,
        payment_request=None,
    ) -> None:
        """
        Validate supporting document target selection.

        Args:
            invoice:
                Optional invoice target.
            payment_request:
                Optional payment request target.

        Raises:
            ValidationError:
                Raised when neither target is supplied or both are
                supplied.
        """
        has_invoice = invoice is not None
        has_payment_request = payment_request is not None

        if not has_invoice and not has_payment_request:
            raise ValidationError(
                "A supporting document must target an invoice or "
                "payment request."
            )

        if has_invoice and has_payment_request:
            raise ValidationError(
                "A supporting document cannot target both an invoice "
                "and a payment request."
            )

    @classmethod
    def create_document(
        cls,
        *,
        website,
        file,
        title: str = "",
        description: str = "",
        invoice=None,
        payment_request=None,
    ) -> SupportingDocument:
        """
        Create a billing supporting document record.

        Args:
            website:
                Tenant website.
            file:
                Uploaded file object.
            title:
                Optional display title.
            description:
                Optional detailed note.
            invoice:
                Optional invoice target.
            payment_request:
                Optional payment request target.

        Returns:
            SupportingDocument:
                Newly created document record.
        """
        cls._validate_target(
            invoice=invoice,
            payment_request=payment_request,
        )

        return SupportingDocument.objects.create(
            website=website,
            invoice=invoice,
            payment_request=payment_request,
            file=file,
            title=title,
            description=description,
        )