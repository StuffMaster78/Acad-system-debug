from django.urls import path
from . import views

urlpatterns = [
    # ── Public read ──────────────────────────────────────────────────────────
    path("", views.legal_document_list, name="legal-list"),
    path("<str:doc_type>/", views.legal_document, name="legal-document"),
    path("<str:doc_type>/agree/", views.record_agreement, name="legal-agree"),

    path("help/categories/", views.help_categories, name="help-categories"),
    path("help/articles/", views.help_articles, name="help-articles"),
    path("help/articles/<slug:slug>/", views.help_article_detail, name="help-article-detail"),

    # ── Admin CRUD (staff only) ───────────────────────────────────────────────
    path("admin/documents/", views.admin_legal_documents, name="admin-legal-documents"),
    path("admin/documents/<int:pk>/", views.admin_legal_document_detail, name="admin-legal-document-detail"),
    path("admin/documents/<int:pk>/activate/", views.admin_activate_document, name="admin-activate-document"),

    path("admin/help/categories/", views.admin_help_categories, name="admin-help-categories"),
    path("admin/help/categories/<int:pk>/", views.admin_help_category_detail, name="admin-help-category-detail"),

    path("admin/help/articles/", views.admin_help_articles, name="admin-help-articles"),
    path("admin/help/articles/<int:pk>/", views.admin_help_article_detail, name="admin-help-article-detail"),
]
