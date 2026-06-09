from django.urls import path

from cms_blog.views import BlogPostHistoryView

app_name = "cms_blog"

urlpatterns = [
    path("<int:page_id>/history/", BlogPostHistoryView.as_view(), name="history"),
]
