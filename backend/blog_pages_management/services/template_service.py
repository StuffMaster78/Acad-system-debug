"""
Service for managing content templates and snippets.
"""
from typing import Dict, Optional
from django.db import transaction

try:
    from ..models import BlogPost
    from ..models.workflow_models import ContentTemplate, ContentSnippet
except ImportError:
    from blog_pages_management.models import BlogPost
    from blog_pages_management.models.workflow_models import ContentTemplate, ContentSnippet

try:
    from service_pages_management.models import ServicePage
except ImportError:
    # Allow using TemplateService in blog-only contexts
    ServicePage = None  # type: ignore[misc]


class TemplateService:
    """Service for managing content templates."""
    
    @staticmethod
    def _build_variables(
        template: ContentTemplate, template_variables: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """Merge default_values with explicit template_variables."""
        variables = template.default_values.copy()
        if template_variables:
            variables.update(template_variables)
        return variables

    @staticmethod
    def _substitute(text: str, variables: Dict[str, str]) -> str:
        """Simple {{var}} substitution helper."""
        if not text:
            return ""
        result = text
        for key, value in variables.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        return result
    
    @staticmethod
    def _resolve_template_inheritance(template: ContentTemplate) -> ContentTemplate:
        """
        Resolve template inheritance chain and merge templates.
        Returns a composite template with all parent templates merged.
        """
        if not template.parent_template:
            return template
        
        # Recursively resolve parent
        parent = TemplateService._resolve_template_inheritance(template.parent_template)
        
        # Create a merged template (virtual, not saved)
        merged = ContentTemplate()
        merged.name = template.name
        merged.description = template.description or parent.description
        merged.template_type = template.template_type
        
        # Merge templates (child overrides parent)
        merged.title_template = template.title_template or parent.title_template
        merged.content_template = template.content_template or parent.content_template
        merged.meta_title_template = template.meta_title_template or parent.meta_title_template
        merged.meta_description_template = template.meta_description_template or parent.meta_description_template
        
        # Merge default values (child overrides parent)
        merged.default_values = {**parent.default_values, **template.default_values}
        
        # Merge template variables
        parent_vars = parent.template_variables or {}
        child_vars = template.template_variables or {}
        merged.template_variables = {**parent_vars, **child_vars}
        
        # Use child's category/tags if set, otherwise parent's
        merged.category = template.category or parent.category
        
        return merged

    @staticmethod
    def create_from_template(
        blog_post: BlogPost,
        template: ContentTemplate,
        template_variables: Dict[str, str] = None,
        use_inheritance: bool = True,
    ) -> BlogPost:
        """
        Create or update a blog post from a template.
        
        Args:
            blog_post: BlogPost instance to update
            template: ContentTemplate to apply
            template_variables: Optional variables to substitute
            use_inheritance: Whether to resolve template inheritance
        
        Returns:
            Updated BlogPost instance
        """
        # Resolve inheritance if enabled
        if use_inheritance and template.parent_template:
            template = TemplateService._resolve_template_inheritance(template)
        
        variables = TemplateService._build_variables(template, template_variables)

        # Apply template
        if template.title_template:
            blog_post.title = TemplateService._substitute(
                template.title_template, variables
            )
        if template.content_template:
            blog_post.content = TemplateService._substitute(
                template.content_template, variables
            )
        if template.meta_title_template:
            blog_post.meta_title = TemplateService._substitute(
                template.meta_title_template, variables
            )
        if template.meta_description_template:
            blog_post.meta_description = TemplateService._substitute(
                template.meta_description_template, variables
            )

        # Apply category and tags
        if template.category:
            blog_post.category = template.category
        if template.tags.exists():
            blog_post.save()  # Need to save first to set M2M
            blog_post.tags.set(template.tags.all())

        # Increment template usage
        template.increment_usage()

        return blog_post

    @staticmethod
    def create_service_page_from_template(
        service_page: "ServicePage",
        template: ContentTemplate,
        template_variables: Dict[str, str] = None,
    ):
        """
        Create or update a service page from a template.

        Applies title/header/content/meta fields using the same variable
        substitution logic as blog templates.
        """
        if ServicePage is None:
            raise RuntimeError("ServicePage model is not available")

        variables = TemplateService._build_variables(template, template_variables)

        # Title & header (default header = title if not customized)
        if template.title_template:
            title_value = TemplateService._substitute(
                template.title_template, variables
            )
            service_page.title = title_value
            # Only override header if it is empty; allows manual headers
            if not getattr(service_page, "header", ""):
                service_page.header = title_value

        if template.content_template:
            service_page.content = TemplateService._substitute(
                template.content_template, variables
            )
        if template.meta_title_template:
            service_page.meta_title = TemplateService._substitute(
                template.meta_title_template, variables
            )
        if template.meta_description_template:
            service_page.meta_description = TemplateService._substitute(
                template.meta_description_template, variables
            )

        template.increment_usage()
        return service_page
    
    @staticmethod
    def insert_snippet(content: str, snippet: ContentSnippet, position: int = -1) -> str:
        """
        Insert a content snippet into existing content.
        
        Args:
            content: Existing content
            position: Position to insert (default: -1 for end)
        
        Returns:
            Updated content with snippet inserted
        """
        snippet.increment_usage()
        
        if position == -1:
            return content + "\n\n" + snippet.content
        elif position == 0:
            return snippet.content + "\n\n" + content
        else:
            lines = content.split('\n')
            lines.insert(position, snippet.content)
            return '\n'.join(lines)


class ExportService:
    """Service for exporting blog posts to various formats."""
    
    @staticmethod
    def export_to_markdown(blog: BlogPost) -> str:
        """Export blog post to Markdown format."""
        md = f"# {blog.title}\n\n"
        
        if blog.meta_description:
            md += f"*{blog.meta_description}*\n\n"
        
        md += f"---\n\n"
        
        # Authors
        if blog.authors.exists():
            authors = ", ".join(author.name for author in blog.authors.all())
            md += f"**Authors:** {authors}\n\n"
        
        # Category and tags
        if blog.category:
            md += f"**Category:** {blog.category.name}\n\n"
        
        if blog.tags.exists():
            tags = ", ".join(tag.name for tag in blog.tags.all())
            md += f"**Tags:** {tags}\n\n"
        
        md += f"---\n\n"
        
        # Content
        md += str(blog.content)
        
        return md
    
    @staticmethod
    def export_to_json(blog: BlogPost) -> Dict:
        """Export blog post to JSON format."""
        from ..serializers import BlogPostSerializer
        
        # Use serializer to get structured data
        serializer = BlogPostSerializer(blog)
        return serializer.data
    
    @staticmethod
    def export_to_html(blog: BlogPost, include_styles: bool = True) -> str:
        """Export blog post to HTML format."""
        html = "<!DOCTYPE html>\n<html>\n<head>\n"
        html += f"<title>{blog.title}</title>\n"
        
        if include_styles:
            html += """<style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1 { color: #333; }
                .meta { color: #666; font-size: 14px; margin-bottom: 20px; }
                .content { line-height: 1.6; }
            </style>\n"""
        
        html += "</head>\n<body>\n"
        html += f"<h1>{blog.title}</h1>\n"
        
        html += "<div class='meta'>\n"
        if blog.authors.exists():
            authors = ", ".join(author.name for author in blog.authors.all())
            html += f"<p><strong>Authors:</strong> {authors}</p>\n"
        if blog.category:
            html += f"<p><strong>Category:</strong> {blog.category.name}</p>\n"
        html += "</div>\n"
        
        html += f"<div class='content'>{blog.content}</div>\n"
        html += "</body>\n</html>"
        
        return html

