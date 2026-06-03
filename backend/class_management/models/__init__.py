from .class_access import (
    ClassAccessDetail,
    ClassAccessGrant,
    ClassAccessLog,
    ClassTwoFactorRequest,
    ClassTwoFactorWindow,
)
from .class_assignment import ClassAssignment
from .class_configs import ClassServiceConfig
from .class_installments import (
    ClassInstallment,
    ClassInstallmentPlan,
)
from .class_order import ClassOrder
from .class_payments import (
    ClassInvoiceLink,
    ClassPaymentAllocation,
)
from .class_pricing import (
    ClassPriceCounterOffer,
    ClassPriceProposal,
)
from .class_scope import (
    ClassScopeAssessment,
    ClassScopeItem,
    ClassTask,
)
from .class_timeline import ClassTimelineEvent
from .class_writer_compensation import ClassWriterCompensation
from .class_portal_work import ClassPortalWorkLog

ClassBundle = ClassOrder
ExpressClass = ClassOrder
ClassBundleInstallment = ClassInstallment

__all__ = [
    "ClassAccessDetail",
    "ClassAccessGrant",
    "ClassAccessLog",
    "ClassAssignment",
    "ClassBundle",
    "ClassBundleInstallment",
    "ClassInstallment",
    "ClassInstallmentPlan",
    "ClassInvoiceLink",
    "ClassOrder",
    "ClassPaymentAllocation",
    "ClassPriceCounterOffer",
    "ClassPriceProposal",
    "ClassScopeAssessment",
    "ClassServiceConfig",
    "ClassScopeItem",
    "ClassTask",
    "ClassTimelineEvent",
    "ClassTwoFactorRequest",
    "ClassTwoFactorWindow",
    "ClassWriterCompensation",
    "ClassPortalWorkLog",
    "ExpressClass",
]
