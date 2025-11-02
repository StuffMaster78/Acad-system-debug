"""
Service for generating Schema.org structured data, Open Graph,
and Twitter Card metadata for maximum Google visibility.
"""
import json
from typing import Dict, List, Optional
from django.utils import timezone
from django.urls import reverse

try:
    from ..models import BlogPost, AuthorProfile
except ImportError:
    from blog_pages_management.models import BlogPost, AuthorProfile
from ..models.seo_models import BlogSEOMetadata, FAQSchema, AuthorSchema


class SEOService:
    """Service for generating SEO metadata and structured data."""
    
    @staticmethod
    def generate_article_schema(blog: BlogPost) -> Dict:
        """
        Generate Schema.org Article/BlogPosting structured data.
        
        Returns:
            Dict with Schema.org Article markup
        """
        authors = blog.authors.all()
        author_data = []
        for author in authors:
            author_schema = {
                "@type": "Person",
                "name": author.name,
            }
            
            # Get author schema data if available
            if hasattr(author, 'schema_data'):
                schema = author.schema_data
                if schema.given_name:
                    author_schema["givenName"] = schema.given_name
                if schema.family_name:
                    author_schema["familyName"] = schema.family_name
                if schema.job_title:
                    author_schema["jobTitle"] = schema.job_title
                if schema.email:
                    author_schema["email"] = schema.email
                if schema.same_as:
                    author_schema["sameAs"] = schema.same_as
            
            author_data.append(author_schema)
        
        article_schema = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": blog.title,
            "description": blog.meta_description or blog.title,
            "image": blog.featured_image.url if blog.featured_image else None,
            "datePublished": blog.publish_date.isoformat() if blog.publish_date else blog.created_at.isoformat(),
            "dateModified": blog.updated_at.isoformat(),
            "author": author_data if author_data else None,
            "publisher": {
                "@type": "Organization",
                "name": blog.website.name,
            }
        }
        
        # Add SEO metadata if available
        if hasattr(blog, 'seo_metadata'):
            seo = blog.seo_metadata
            if seo.article_type:
                article_schema["@type"] = seo.article_type
            if seo.article_section:
                article_schema["articleSection"] = seo.article_section
            if seo.keywords:
                article_schema["keywords"] = seo.keywords
            if seo.schema_organization:
                article_schema["publisher"].update(seo.schema_organization)
        
        return article_schema
    
    @staticmethod
    def generate_faq_schema(blog: BlogPost) -> Optional[Dict]:
        """
        Generate Schema.org FAQPage structured data from blog FAQs.
        
        Returns:
            Dict with Schema.org FAQPage markup or None
        """
        # Try FAQSchema first (enhanced model)
        faqs = FAQSchema.objects.filter(blog=blog).order_by('display_order', 'is_featured')
        
        # Fallback to BlogFAQ if FAQSchema doesn't exist
        if not faqs.exists():
            try:
                from ..models import BlogFAQ
            except ImportError:
                from blog_pages_management.models import BlogFAQ
            blog_faqs = BlogFAQ.objects.filter(blog=blog)
            if not blog_faqs.exists():
                return None
            
            faq_items = []
            for faq in blog_faqs:
                faq_items.append({
                    "@type": "Question",
                    "name": faq.question,
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": faq.answer
                    }
                })
        else:
            faq_items = []
            for faq in faqs:
                item = {
                    "@type": "Question",
                    "name": faq.question,
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": faq.answer
                    }
                }
                
                if faq.date_created:
                    item["dateCreated"] = faq.date_created.isoformat()
                if faq.date_modified:
                    item["dateModified"] = faq.date_modified.isoformat()
                if faq.author_name:
                    item["author"] = {
                        "@type": "Person",
                        "name": faq.author_name
                    }
                if faq.upvote_count > 0:
                    item["upvoteCount"] = faq.upvote_count
                
                faq_items.append(item)
        
        if not faq_items:
            return None
        
        faq_schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": faq_items
        }
        
        return faq_schema
    
    @staticmethod
    def generate_category_schema(category) -> Optional[Dict]:
        """
        Generate Schema.org CollectionPage structured data for blog categories.
        
        Returns:
            Dict with Schema.org CollectionPage markup or None
        """
        if not category:
            return None
        
        category_schema = {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": category.name,
            "description": category.meta_description or category.description or f"Blog posts in {category.name} category",
            "url": f"{category.website.domain}/blog/category/{category.slug}",
        }
        
        if category.category_image:
            category_schema["image"] = category.category_image.url
        
        return category_schema
    
    @staticmethod
    def generate_breadcrumb_schema(blog: BlogPost) -> Dict:
        """
        Generate Schema.org BreadcrumbList structured data.
        
        Returns:
            Dict with Schema.org BreadcrumbList markup
        """
        breadcrumb_items = [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "Home",
                "item": blog.website.domain  # Adjust to actual homepage URL
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": "Blog",
                "item": f"{blog.website.domain}/blog"  # Adjust to actual blog listing URL
            }
        ]
        
        if blog.category:
            breadcrumb_items.append({
                "@type": "ListItem",
                "position": 3,
                "name": blog.category.name,
                "item": f"{blog.website.domain}/blog/category/{blog.category.slug}"
            })
        
        breadcrumb_items.append({
            "@type": "ListItem",
            "position": len(breadcrumb_items) + 1,
            "name": blog.title,
            "item": f"{blog.website.domain}/blog/{blog.slug}"
        })
        
        breadcrumb_schema = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": breadcrumb_items
        }
        
        return breadcrumb_schema
    
    @staticmethod
    def generate_author_schema(author: AuthorProfile) -> Dict:
        """
        Generate Schema.org Person structured data for an author.
        
        Returns:
            Dict with Schema.org Person markup
        """
        author_schema = {
            "@context": "https://schema.org",
            "@type": "Person",
            "name": author.name,
        }
        
        if hasattr(author, 'schema_data'):
            schema = author.schema_data
            
            if schema.given_name:
                author_schema["givenName"] = schema.given_name
            if schema.family_name:
                author_schema["familyName"] = schema.family_name
            if schema.job_title:
                author_schema["jobTitle"] = schema.job_title
            if schema.works_for:
                author_schema["worksFor"] = {
                    "@type": "Organization",
                    "name": schema.works_for
                }
            if schema.email:
                author_schema["email"] = schema.email
            if schema.telephone:
                author_schema["telephone"] = schema.telephone
            if schema.address:
                author_schema["address"] = {
                    "@type": "PostalAddress",
                    **schema.address
                }
            if schema.same_as:
                author_schema["sameAs"] = schema.same_as
            if schema.knows_about:
                author_schema["knowsAbout"] = schema.knows_about
        
        if author.profile_picture:
            author_schema["image"] = author.profile_picture.url
        
        if author.bio:
            author_schema["description"] = author.bio
        
        return author_schema
    
    @staticmethod
    def get_all_schemas_for_blog(blog: BlogPost) -> Dict[str, Dict]:
        """
        Get all Schema.org structured data for a blog post.
        
        Returns:
            Dict with all schema types
        """
        schemas = {
            "article": SEOService.generate_article_schema(blog),
            "breadcrumb": SEOService.generate_breadcrumb_schema(blog),
        }
        
        # Add FAQ schema if FAQs exist
        faq_schema = SEOService.generate_faq_schema(blog)
        if faq_schema:
            schemas["faq"] = faq_schema
        
        return schemas
    
    @staticmethod
    def render_schema_script_tags(blog: BlogPost) -> str:
        """
        Render Schema.org structured data as JSON-LD script tags.
        
        Returns:
            HTML string with script tags
        """
        schemas = SEOService.get_all_schemas_for_blog(blog)
        
        script_tags = []
        for schema_type, schema_data in schemas.items():
            if schema_data:
                script_tags.append(
                    f'<script type="application/ld+json">\n{json.dumps(schema_data, indent=2)}\n</script>'
                )
        
        return '\n'.join(script_tags)
    
    @staticmethod
    def get_open_graph_tags(blog: BlogPost) -> Dict[str, str]:
        """
        Get Open Graph meta tags for social sharing.
        
        Returns:
            Dict with OG tag names and values
        """
        if hasattr(blog, 'seo_metadata') and blog.seo_metadata.og_title:
            seo = blog.seo_metadata
            og_title = seo.og_title
            og_description = seo.og_description or blog.meta_description
            og_image = seo.og_image.url if seo.og_image else None
            og_url = seo.og_url or f"{blog.website.domain}/blog/{blog.slug}"
        else:
            og_title = blog.meta_title or blog.title
            og_description = blog.meta_description or blog.title
            og_image = blog.featured_image.url if blog.featured_image else None
            og_url = f"{blog.website.domain}/blog/{blog.slug}"
        
        og_tags = {
            "og:type": "article",
            "og:title": og_title,
            "og:description": og_description,
            "og:url": og_url,
        }
        
        if og_image:
            og_tags["og:image"] = og_image
        
        if hasattr(blog, 'seo_metadata'):
            seo = blog.seo_metadata
            if seo.og_site_name:
                og_tags["og:site_name"] = seo.og_site_name
        
        # Add article-specific tags
        if blog.publish_date:
            og_tags["article:published_time"] = blog.publish_date.isoformat()
        og_tags["article:modified_time"] = blog.updated_at.isoformat()
        
        # Add authors
        authors = blog.authors.all()
        for author in authors:
            if not og_tags.get("article:author"):
                og_tags["article:author"] = []
            og_tags["article:author"].append(author.name)
        
        return og_tags
    
    @staticmethod
    def get_twitter_card_tags(blog: BlogPost) -> Dict[str, str]:
        """
        Get Twitter Card meta tags.
        
        Returns:
            Dict with Twitter Card tag names and values
        """
        if hasattr(blog, 'seo_metadata') and blog.seo_metadata.twitter_title:
            seo = blog.seo_metadata
            twitter_card_type = seo.twitter_card_type
            twitter_title = seo.twitter_title
            twitter_description = seo.twitter_description or blog.meta_description
            twitter_image = seo.twitter_image.url if seo.twitter_image else None
            twitter_site = seo.twitter_site
            twitter_creator = seo.twitter_creator
        else:
            twitter_card_type = "summary_large_image"
            twitter_title = blog.meta_title or blog.title
            twitter_description = blog.meta_description or blog.title
            twitter_image = blog.featured_image.url if blog.featured_image else None
            twitter_site = None
            twitter_creator = None
        
        twitter_tags = {
            "twitter:card": twitter_card_type,
            "twitter:title": twitter_title,
            "twitter:description": twitter_description,
        }
        
        if twitter_image:
            twitter_tags["twitter:image"] = twitter_image
        
        if twitter_site:
            twitter_tags["twitter:site"] = twitter_site
        
        if twitter_creator:
            twitter_tags["twitter:creator"] = twitter_creator
        
        return twitter_tags

