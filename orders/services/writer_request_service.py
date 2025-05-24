from orders.models import WriterRequest
from audit_logging.services import log_audit_action
from django.utils import timezone

class WriterRequestService:

    @staticmethod
    def create_request(order, writer, request_type, reason, data):
        request = WriterRequest.objects.create(
            order=order,
            website=order.website,
            request_type=request_type,
            requested_by_writer=writer,
            request_reason=reason,
            new_deadline=data.get('new_deadline'),
            additional_pages=data.get('additional_pages'),
            additional_slides=data.get('additional_slides'),
        )

        log_audit_action(
            actor=writer,
            action="CREATE_WRITER_REQUEST",
            target="orders.WriterRequest",
            target_id=request.id,
            metadata={"request_type": request_type, "data": data}
        )

        return request

    @staticmethod
    def client_respond(request, client, approve, reason=None):
        if request.status != 'pending':
            raise ValueError("Request already handled.")

        if approve:
            request.client_approval = True
            request.status = 'accepted'
            WriterRequestService._apply_request_changes(request)
        else:
            request.status = 'declined'

        request.save()

        log_audit_action(
            actor=client,
            action="CLIENT_RESPOND_WRITER_REQUEST",
            target="orders.WriterRequest",
            target_id=request.id,
            metadata={"approved": approve, "reason": reason}
        )

    @staticmethod
    def admin_override(request, admin, new_deadline=None):
        request.admin_approval = True
        request.status = 'accepted'

        if new_deadline:
            request.new_deadline = new_deadline

        WriterRequestService._apply_request_changes(request)
        request.save()

        log_audit_action(
            actor=admin,
            action="ADMIN_OVERRIDE_WRITER_REQUEST",
            target="orders.WriterRequest",
            target_id=request.id,
            metadata={"new_deadline": new_deadline}
        )

    @staticmethod
    def _apply_request_changes(request):
        order = request.order
        if request.request_type == 'deadline_extension' and request.new_deadline:
            order.deadline = request.new_deadline
        if request.request_type == 'page_increase' and request.additional_pages:
            order.pages += request.additional_pages
        if request.request_type == 'slide_increase' and request.additional_slides:
            order.slides += request.additional_slides
        order.save()
