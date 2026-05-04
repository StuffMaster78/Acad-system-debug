from __future__ import annotations

from django.db import models


class ClassOrderStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    SUBMITTED = "submitted", "Submitted"
    NEEDS_CLIENT_INFO = "needs_client_info", "Needs Client Info"
    UNDER_REVIEW = "under_review", "Under Review"
    PRICE_PROPOSED = "price_proposed", "Price Proposed"
    NEGOTIATING = "negotiating", "Negotiating"
    ACCEPTED = "accepted", "Accepted"
    PENDING_PAYMENT = "pending_payment", "Pending Payment"
    PARTIALLY_PAID = "partially_paid", "Partially Paid"
    PAID = "paid", "Paid"
    ASSIGNED = "assigned", "Assigned"
    IN_PROGRESS = "in_progress", "In Progress"
    PAUSED = "paused", "Paused"
    QUALITY_REVIEW = "quality_review", "Quality Review"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"
    ARCHIVED = "archived", "Archived"


class ClassPaymentStatus(models.TextChoices):
    UNPAID = "unpaid", "Unpaid"
    PARTIALLY_PAID = "partially_paid", "Partially Paid"
    PAID = "paid", "Paid"
    OVERDUE = "overdue", "Overdue"
    REFUNDED = "refunded", "Refunded"


class ClassProposalStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    SENT = "sent", "Sent"
    COUNTERED = "countered", "Countered"
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"
    EXPIRED = "expired", "Expired"
    CANCELLED = "cancelled", "Cancelled"


class ClassInstallmentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    DUE = "due", "Due"
    OVERDUE = "overdue", "Overdue"
    PAID = "paid", "Paid"
    WAIVED = "waived", "Waived"
    CANCELLED = "cancelled", "Cancelled"


class ClassTaskStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    ASSIGNED = "assigned", "Assigned"
    IN_PROGRESS = "in_progress", "In Progress"
    SUBMITTED = "submitted", "Submitted"
    APPROVED = "approved", "Approved"
    REVISION_REQUESTED = "revision_requested", "Revision Requested"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class ClassItemType(models.TextChoices):
    DISCUSSION_POST = "discussion_post", "Discussion Post"
    DISCUSSION_RESPONSE = "discussion_response", "Discussion Response"

    QUIZ = "quiz", "Quiz"
    EXAM = "exam", "Exam"
    MIDTERM = "midterm", "Midterm"
    FINAL_EXAM = "final_exam", "Final Exam"

    ASSIGNMENT = "assignment", "Assignment"
    ESSAY = "essay", "Essay"
    ARTICLE_REVIEW = "article_review", "Article Review"
    ANNOTATED_BIBLIOGRAPHY = (
        "annotated_bibliography",
        "Annotated Bibliography",
    )
    BOOK_REVIEW = "book_review", "Book Review"
    CASE_STUDY = "case_study", "Case Study"
    COURSEWORK = "coursework", "Coursework"
    CREATIVE_WRITING = "creative_writing", "Creative Writing"
    CRITICAL_REVIEW = "critical_review", "Critical Review"
    REFLECTION_PAPER = "reflection_paper", "Reflection Paper"
    RESEARCH_PAPER = "research_paper", "Research Paper"
    TERM_PAPER = "term_paper", "Term Paper"
    THESIS_CHAPTER = "thesis_chapter", "Thesis Chapter"

    PROJECT = "project", "Project"
    CAPSTONE_PROJECT = "capstone_project", "Capstone Project"
    GROUP_PROJECT = "group_project", "Group Project"
    PORTFOLIO = "portfolio", "Portfolio"

    PRESENTATION = "presentation", "Presentation"
    PPT_SLIDES = "ppt_slides", "PowerPoint Slides"
    POSTER = "poster", "Poster"
    INFOGRAPHIC = "infographic", "Infographic"

    LAB = "lab", "Lab Work"
    LAB_REPORT = "lab_report", "Lab Report"
    PRACTICUM = "practicum", "Practicum"
    FIELD_REPORT = "field_report", "Field Report"

    CALCULATION_TASK = "calculation_task", "Calculation Task"
    CODING_TASK = "coding_task", "Coding Task"
    DATA_ANALYSIS = "data_analysis", "Data Analysis"
    SPSS_TASK = "spss_task", "SPSS Task"
    EXCEL_TASK = "excel_task", "Excel Task"

    JOURNAL_ENTRY = "journal_entry", "Journal Entry"
    WEEKLY_TASK = "weekly_task", "Weekly Task"
    ONLINE_ACTIVITY = "online_activity", "Online Activity"

    OTHER = "other", "Other"


class ClassComplexityLevel(models.TextChoices):
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"
    VERY_HIGH = "very_high", "Very High"


class ClassAccessGrantStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    REVOKED = "revoked", "Revoked"
    EXPIRED = "expired", "Expired"


class TwoFactorRequestStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SENT = "sent", "Sent"
    RESOLVED = "resolved", "Resolved"
    CANCELLED = "cancelled", "Cancelled"
    EXPIRED = "expired", "Expired"


class ClassAssignmentStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    REASSIGNED = "reassigned", "Reassigned"
    REMOVED = "removed", "Removed"
    COMPLETED = "completed", "Completed"


class ClassWriterCompensationType(models.TextChoices):
    PERCENTAGE = "percentage", "Percentage"
    FIXED_AMOUNT = "fixed_amount", "Fixed Amount"


class ClassWriterCompensationStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    APPROVED = "approved", "Approved"
    EARNED = "earned", "Earned"
    POSTED_TO_WALLET = "posted_to_wallet", "Posted To Wallet"
    CANCELLED = "cancelled", "Cancelled"


class ClassPaymentSourceType(models.TextChoices):
    WALLET = "wallet", "Wallet"
    EXTERNAL = "external", "External"
    SPLIT = "split", "Split"


class ClassTimelineEventType(models.TextChoices):
    CREATED = "created", "Created"
    UPDATED = "updated", "Updated"
    SUBMITTED = "submitted", "Submitted"
    NEEDS_CLIENT_INFO = "needs_client_info", "Needs Client Info"
    REVIEW_STARTED = "review_started", "Review Started"
    PRICE_PROPOSED = "price_proposed", "Price Proposed"
    PRICE_ACCEPTED = "price_accepted", "Price Accepted"    
    PRICE_REJECTED = "price_rejected", "Price Rejected"
    COUNTER_OFFER_SENT = "counter_offer_sent", "Counter Offer Sent"
    INVOICE_CREATED = "invoice_created", "Invoice Created"
    PAYMENT_APPLIED = "payment_applied", "Payment Applied"
    INSTALLMENT_OVERDUE = "installment_overdue", "Installment Overdue"
    WRITER_ASSIGNED = "writer_assigned", "Writer Assigned"
    WORK_STARTED = "work_started", "Work Started"
    WORK_PAUSED = "work_paused", "Work Paused"
    QUALITY_REVIEW_STARTED = (
        "quality_review_started",
        "Quality Review Started",
    )
    TASK_CREATED = "task_created", "Task Created"
    TASK_COMPLETED = "task_completed", "Task Completed"
    ACCESS_VIEWED = "access_viewed", "Access Viewed"
    TWO_FACTOR_REQUESTED = "two_factor_requested", "2FA Requested"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"
    ARCHIVED = "archived", "Archived"

class ClassFileCategory(models.TextChoices):
    CLIENT_UPLOAD = "client_upload", "Client Upload"
    WRITER_UPLOAD = "writer_upload", "Writer Upload"
    PORTAL_DOWNLOAD = "portal_download", "Portal Download"
    PORTAL_UPLOAD = "portal_upload", "Portal Upload"
    FINAL_DELIVERABLE = "final_deliverable", "Final Deliverable"
    SUPPORTING_MATERIAL = "supporting_material", "Supporting Material"
    ACCESS_RELATED = "access_related", "Access Related"
    ADMIN_INTERNAL = "admin_internal", "Admin Internal"

class ClassPortalActivityType(models.TextChoices):
    LOGGED_IN = "logged_in", "Logged In"
    COURSE_REVIEWED = "course_reviewed", "Course Reviewed"
    MODULE_REVIEWED = "module_reviewed", "Module Reviewed"
    DISCUSSION_POSTED = "discussion_posted", "Discussion Posted"
    RESPONSE_POSTED = "response_posted", "Response Posted"
    QUIZ_COMPLETED = "quiz_completed", "Quiz Completed"
    EXAM_COMPLETED = "exam_completed", "Exam Completed"
    ASSIGNMENT_SUBMITTED = "assignment_submitted", "Assignment Submitted"
    FILE_UPLOADED = "file_uploaded", "File Uploaded"
    GRADE_CHECKED = "grade_checked", "Grade Checked"
    MESSAGE_CHECKED = "message_checked", "Message Checked"
    ACCESS_ISSUE_FOUND = "access_issue_found", "Access Issue Found"
    TWO_FACTOR_NEEDED = "two_factor_needed", "2FA Needed"
    OTHER = "other", "Other"


class ClassPortalWorkLogVerificationStatus(models.TextChoices):
    UNVERIFIED = "unverified", "Unverified"
    VERIFIED = "verified", "Verified"
    REJECTED = "rejected", "Rejected"