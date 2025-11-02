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


class TemplateService:
    """Service for managing content templates."""
    
    @staticmethod
    def create_from_template(
        blog_post: BlogPost,
        template: ContentTemplate,
        template_variables: Dict[str, str] = None
    ) -> BlogPost:
        """
        Create or update a blog post from a template.
        
        Args:
            blog_post: BlogPost instance (can be new)
            template: ContentTemplate to use
            template_variables: Variables to substitute in template
        
        Returns:
            Updated BlogPost instance
        """
        variables = template.default_values.copy()
        if template_variables:
            variables.update(template_variables)
        
        # Substitute variables in templates
        def substitute(text: str) -> str:
            if not text:
                return ""
            result = text
            for key, value in variables.items():
                result = result.replace(f"{{{{{key}}}}}", str(value))
            return result
        
        # Apply template
        if template.title_template:
            blog_post.title = substitute(template.title_template)
        if template.content_template:
            blog_post.content = substitute(template.content_template)
        if template.meta_title_template:
            blog_post.meta_title = substitute(template.meta_title_template)
        if template.meta_description_template:
            blog_post.meta_description = substitute(template.meta_description_template)
        
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

