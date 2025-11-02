"""
SEO service for service pages - Schema.org structured data generation.
"""
import json
from typing import Dict, Optional
from django.utils import timezone

try:
    from ..models import ServicePage
    from ..models.enhanced_models import (
        ServicePageSEOMetadata, ServicePageFAQ, ServicePageResource
    )
except ImportError:
    from service_pages_management.models import ServicePage
    from service_pages_management.models.enhanced_models import (
        ServicePageSEOMetadata, ServicePageFAQ, ServicePageResource
    )


class ServicePageSEOService:
    """Service for generating SEO metadata and structured data for service pages."""
    
    @staticmethod
    def generate_webpage_schema(service_page: ServicePage) -> Dict:
        """
        Generate Schema.org WebPage structured data for service pages.
        
        Returns:
            Dict with Schema.org WebPage markup
        """
        webpage_schema = {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": service_page.title,
            "description": service_page.meta_description or service_page.content[:200],
            "url": f"{service_page.website.domain}/{service_page.slug}",
            "datePublished": service_page.publish_date.isoformat() if service_page.publish_date else service_page.created_at.isoformat(),
            "dateModified": service_page.updated_at.isoformat(),
            "publisher": {
                "@type": "Organization",
                "name": service_page.website.name,
            },
            "mainEntity": {
                "@type": "Service",
                "name": service_page.title,
                "description": service_page.content[:500] if len(service_page.content) > 500 else service_page.content,
            }
        }
        
        # Add SEO metadata if available
        if hasattr(service_page, 'seo_metadata'):
            seo = service_page.seo_metadata
            if seo.article_type:
                webpage_schema["@type"] = seo.article_type
            
            if seo.schema_organization:
                webpage_schema["publisher"].update(seo.schema_organization)
        
        # Add breadcrumb
        breadcrumb = ServicePageSEOService.generate_breadcrumb_schema(service_page)
        if breadcrumb:
            webpage_schema["breadcrumb"] = breadcrumb
        
        return webpage_schema
    
    @staticmethod
    def generate_service_schema(service_page: ServicePage) -> Dict:
        """
        Generate Schema.org Service structured data.
        
        Returns:
            Dict with Schema.org Service markup
        """
        service_schema = {
            "@context": "https://schema.org",
            "@type": "Service",
            "name": service_page.title,
            "description": service_page.meta_description or service_page.content[:200],
            "provider": {
                "@type": "Organization",
                "name": service_page.website.name,
            },
            "areaServed": {
                "@type": "Country",
                "name": "US"  # Default, can be made configurable
            }
        }
        
        # Add image if available
        if service_page.image:
            service_schema["image"] = service_page.image.url
        
        # Add resources
        resources = ServicePageResource.objects.filter(service_page=service_page)
        if resources.exists():
            service_schema["hasOfferCatalog"] = {
                "@type": "OfferCatalog",
                "name": f"{service_page.title} Resources",
                "itemListElement": [
                    {
                        "@type": "Offer",
                        "itemOffered": {
                            "@type": "Service",
                            "name": resource.title,
                            "url": resource.url
                        }
                    }
                    for resource in resources
                ]
            }
        
        return service_schema
    
    @staticmethod
    def generate_faq_schema(service_page: ServicePage) -> Optional[Dict]:
        """
        Generate Schema.org FAQPage structured data from service page FAQs.
        
        Returns:
            Dict with Schema.org FAQPage markup or None
        """
        faqs = ServicePageFAQ.objects.filter(service_page=service_page).order_by('display_order', 'is_featured')
        
        if not faqs.exists():
            return None
        
        faq_items = []
        for faq in faqs:
            faq_items.append({
                "@type": "Question",
                "name": faq.question,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": faq.answer
                }
            })
        
        faq_schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": faq_items
        }
        
        return faq_schema
    
    @staticmethod
    def generate_breadcrumb_schema(service_page: ServicePage) -> Optional[Dict]:
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
                "item": service_page.website.domain
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": "Services",
                "item": f"{service_page.website.domain}/services"
            },
            {
                "@type": "ListItem",
                "position": 3,
                "name": service_page.title,
                "item": f"{service_page.website.domain}/{service_page.slug}"
            }
        ]
        
        breadcrumb_schema = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": breadcrumb_items
        }
        
        return breadcrumb_schema
    
    @staticmethod
    def get_all_schemas_for_service_page(service_page: ServicePage) -> Dict[str, Dict]:
        """
        Get all Schema.org structured data for a service page.
        
        Returns:
            Dict with all schema types
        """
        schemas = {
            "webpage": ServicePageSEOService.generate_webpage_schema(service_page),
            "service": ServicePageSEOService.generate_service_schema(service_page),
            "breadcrumb": ServicePageSEOService.generate_breadcrumb_schema(service_page),
        }
        
        # Add FAQ schema if FAQs exist
        faq_schema = ServicePageSEOService.generate_faq_schema(service_page)
        if faq_schema:
            schemas["faq"] = faq_schema
        
        return schemas
    
    @staticmethod
    def render_schema_script_tags(service_page: ServicePage) -> str:
        """
        Render Schema.org structured data as JSON-LD script tags.
        
        Returns:
            HTML string with script tags
        """
        schemas = ServicePageSEOService.get_all_schemas_for_service_page(service_page)
        
        script_tags = []
        for schema_type, schema_data in schemas.items():
            if schema_data:
                script_tags.append(
                    f'<script type="application/ld+json">\n{json.dumps(schema_data, indent=2)}\n</script>'
                )
        
        return '\n'.join(script_tags)
    
    @staticmethod
    def get_open_graph_tags(service_page: ServicePage) -> Dict[str, str]:
        """
        Get Open Graph meta tags for social sharing.
        
        Returns:
            Dict with OG tag names and values
        """
        if hasattr(service_page, 'seo_metadata') and service_page.seo_metadata.og_title:
            seo = service_page.seo_metadata
            og_title = seo.og_title
            og_description = seo.og_description or service_page.meta_description
            og_image = seo.og_image.url if seo.og_image else None
        else:
            og_title = service_page.meta_title or service_page.title
            og_description = service_page.meta_description or service_page.content[:200]
            og_image = service_page.og_image.url if service_page.og_image else (service_page.image.url if service_page.image else None)
        
        og_tags = {
            "og:type": "website",
            "og:title": og_title,
            "og:description": og_description,
            "og:url": f"{service_page.website.domain}/{service_page.slug}",
        }
        
        if og_image:
            og_tags["og:image"] = og_image
        
        if hasattr(service_page, 'seo_metadata'):
            seo = service_page.seo_metadata
            if seo.og_site_name:
                og_tags["og:site_name"] = seo.og_site_name
        
        return og_tags
    
    @staticmethod
    def get_twitter_card_tags(service_page: ServicePage) -> Dict[str, str]:
        """
        Get Twitter Card meta tags.
        
        Returns:
            Dict with Twitter Card tag names and values
        """
        if hasattr(service_page, 'seo_metadata') and service_page.seo_metadata.twitter_title:
            seo = service_page.seo_metadata
            twitter_card_type = seo.twitter_card_type
            twitter_title = seo.twitter_title
            twitter_description = seo.twitter_description or service_page.meta_description
            twitter_image = seo.twitter_image.url if seo.twitter_image else None
        else:
            twitter_card_type = "summary_large_image"
            twitter_title = service_page.meta_title or service_page.title
            twitter_description = service_page.meta_description or service_page.content[:200]
            twitter_image = service_page.og_image.url if service_page.og_image else (service_page.image.url if service_page.image else None)
        
        twitter_tags = {
            "twitter:card": twitter_card_type,
            "twitter:title": twitter_title,
            "twitter:description": twitter_description,
        }
        
        if twitter_image:
            twitter_tags["twitter:image"] = twitter_image
        
        return twitter_tags

