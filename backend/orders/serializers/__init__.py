"""
Serializers package for orders app.
This __init__.py imports all serializers from the legacy serializers.py file
to maintain backward compatibility, and also exports serializers from submodules.
"""
# Import all serializers from the legacy serializers_legacy.py file
# This maintains backward compatibility with existing imports like:
# from orders.serializers import OrderSerializer
import importlib.util
import sys
from pathlib import Path

# Get the parent directory (orders/)
_parent_dir = Path(__file__).parent.parent

# Load the legacy serializers module
_legacy_path = _parent_dir / 'serializers_legacy.py'
if _legacy_path.exists():
    spec = importlib.util.spec_from_file_location("orders.serializers_legacy", _legacy_path)
    _legacy_module = importlib.util.module_from_spec(spec)
    sys.modules["orders.serializers_legacy"] = _legacy_module
    spec.loader.exec_module(_legacy_module)
    
    # Import everything from the legacy module
    for name in dir(_legacy_module):
        if not name.startswith('_'):
            setattr(sys.modules[__name__], name, getattr(_legacy_module, name))

# Also export serializers from submodules
from orders.serializers.progress import (
    WriterProgressSerializer,
    WriterProgressListSerializer
)
from orders.serializers.draft_requests import (
    DraftRequestSerializer,
    DraftRequestCreateSerializer,
    DraftFileSerializer,
)
from orders.serializers.order_templates import (
    OrderTemplateSerializer,
    OrderTemplateCreateSerializer,
    OrderFromTemplateSerializer,
)
from orders.serializers.order_drafts import (
    OrderDraftSerializer,
    OrderDraftCreateSerializer,
    OrderDraftConvertSerializer,
)
from orders.serializers.order_presets import (
    OrderPresetSerializer,
    OrderPresetApplySerializer,
)
from orders.serializers.enhanced_revisions import (
    RevisionRequestSerializer,
    RevisionRequestCreateSerializer,
    RevisionRequestUpdateSerializer,
    RevisionRequestCompleteSerializer,
)
from orders.serializers.writer_acknowledgment import (
    WriterAssignmentAcknowledgmentSerializer,
)
from orders.serializers.message_reminders import (
    MessageReminderSerializer,
)
from orders.serializers.review_reminders import (
    ReviewReminderSerializer,
)

