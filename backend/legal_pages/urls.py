from django.urls import path
from . import views

urlpatterns = [
    # Legal documents (public read)
    path("", views.legal_document_list, name="legal-list"),
    path("<str:doc_type>/", views.legal_document, name="legal-document"),
    path("<str:doc_type>/agree/", views.record_agreement, name="legal-agree"),

    # Help center (public read)
    path("help/categories/", views.help_categories, name="help-categories"),
    path("help/articles/", views.help_articles, name="help-articles"),
    path("help/articles/<slug:slug>/", views.help_article_detail, name="help-article-detail"),
]
