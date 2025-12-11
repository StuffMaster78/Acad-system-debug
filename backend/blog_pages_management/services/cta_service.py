"""
Service for managing CTAs and content blocks in blog posts.
Handles automatic insertion, placement, and tracking.
"""
from typing import List, Dict, Optional
from django.db import transaction
from django.utils import timezone

from ..models.content_blocks import (
    CTABlock, BlogCTAPlacement, ContentBlockTemplate, BlogContentBlock
)
try:
    from ..models import BlogPost
except ImportError:
    from blog_pages_management.models import BlogPost


class CTAService:
    """Service for managing CTAs in blog posts."""
    
    @staticmethod
    @transaction.atomic
    def place_cta_in_blog(
        blog: BlogPost,
        cta_block: CTABlock,
        placement_type: str = 'manual',
        position: int = 0,
        display_conditions: Optional[Dict] = None
    ) -> BlogCTAPlacement:
        """
        Place a CTA in a blog post.
        
        Args:
            blog: BlogPost instance
            cta_block: CTABlock instance
            placement_type: Type of placement (auto_top, auto_middle, auto_bottom, etc.)
            position: Position in content (paragraph/heading index)
            display_conditions: Optional conditions for displaying CTA
        
        Returns:
            BlogCTAPlacement instance
        """
        placement, created = BlogCTAPlacement.objects.get_or_create(
            blog=blog,
            cta_block=cta_block,
            placement_type=placement_type,
            position=position,
            defaults={
                'is_active': True,
                'display_conditions': display_conditions or {}
            }
        )
        
        if not created:
            placement.is_active = True
            if display_conditions:
                placement.display_conditions = display_conditions
            placement.save()
        
        return placement
    
    @staticmethod
    @transaction.atomic
    def auto_insert_ctas(blog: BlogPost, cta_blocks: List[CTABlock] = None) -> List[BlogCTAPlacement]:
        """
        Automatically insert CTAs into a blog post at strategic positions.
        
        Args:
            blog: BlogPost instance
            cta_blocks: Optional list of CTAs to use (if None, uses active CTAs from blog's website)
        
        Returns:
            List of created BlogCTAPlacement instances
        """
        if not cta_blocks:
            cta_blocks = list(CTABlock.objects.filter(
                website=blog.website,
                is_active=True
            ).order_by('display_order')[:3])  # Limit to 3 CTAs
        
        placements = []
        
        # Insert top CTA
        if len(cta_blocks) > 0:
            placements.append(
                CTAService.place_cta_in_blog(
                    blog=blog,
                    cta_block=cta_blocks[0],
                    placement_type='auto_top',
                    position=0
                )
            )
        
        # Insert middle CTA (calculate position based on content length)
        if len(cta_blocks) > 1:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(blog.content, 'html.parser')
            paragraphs = soup.find_all('p')
            middle_position = len(paragraphs) // 2 if paragraphs else 0
            
            placements.append(
                CTAService.place_cta_in_blog(
                    blog=blog,
                    cta_block=cta_blocks[1],
                    placement_type='auto_middle',
                    position=middle_position
                )
            )
        
        # Insert bottom CTA
        if len(cta_blocks) > 2:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(blog.content, 'html.parser')
            paragraphs = soup.find_all('p')
            bottom_position = len(paragraphs) if paragraphs else 0
            
            placements.append(
                CTAService.place_cta_in_blog(
                    blog=blog,
                    cta_block=cta_blocks[2],
                    placement_type='auto_bottom',
                    position=bottom_position
                )
            )
        
        return placements
    
    @staticmethod
    def track_cta_click(placement: BlogCTAPlacement, user=None, ip_address: str = None):
        """Track a click on a CTA placement."""
        placement.click_count += 1
        placement.save(update_fields=['click_count'])
        
        # Also track on CTA block itself
        cta_block = placement.cta_block
        # Could add click tracking to CTABlock if needed
    
    @staticmethod
    def track_cta_conversion(placement: BlogCTAPlacement, user=None):
        """Track a conversion from a CTA placement."""
        placement.conversion_count += 1
        placement.save(update_fields=['conversion_count'])


class ContentBlockService:
    """Service for managing content blocks in blog posts."""
    
    @staticmethod
    @transaction.atomic
    def insert_content_block(
        blog: BlogPost,
        template: ContentBlockTemplate,
        position: int,
        custom_data: Optional[Dict] = None,
        auto_insert: bool = False
    ) -> BlogContentBlock:
        """
        Insert a content block into a blog post.
        
        Args:
            blog: BlogPost instance
            template: ContentBlockTemplate instance
            position: Position in content
            custom_data: Optional custom data overriding template data
            auto_insert: Whether this was auto-inserted
        
        Returns:
            BlogContentBlock instance
        """
        block = BlogContentBlock.objects.create(
            blog=blog,
            template=template,
            position=position,
            custom_data=custom_data or {},
            auto_insert=auto_insert,
            is_active=True
        )
        return block
    
    @staticmethod
    def auto_insert_table_of_contents(blog: BlogPost) -> Optional[BlogContentBlock]:
        """
        Auto-insert a table of contents block if the blog has headings.
        """
        if not blog.toc or len(blog.toc) == 0:
            return None
        
        # Check if TOC template exists
        toc_template = ContentBlockTemplate.objects.filter(
            website=blog.website,
            block_type='table',
            name__icontains='table of contents'
        ).first()
        
        if not toc_template:
            return None
        
        return ContentBlockService.insert_content_block(
            blog=blog,
            template=toc_template,
            position=0,  # Insert at top
            custom_data={'toc': blog.toc},
            auto_insert=True
        )
    
    @staticmethod
    def get_rendered_content(blog: BlogPost) -> str:
        """
        Get blog content with all content blocks inserted.
        
        Returns:
            Rendered HTML with content blocks inserted
        """
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(blog.content, 'html.parser')
        content_blocks = BlogContentBlock.objects.filter(
            blog=blog,
            is_active=True
        ).order_by('position')
        
        paragraphs = soup.find_all('p')
        
        # Insert content blocks at their positions
        for block in reversed(content_blocks):  # Reverse to maintain positions
            if block.position < len(paragraphs):
                block_html = f'<div class="content-block {block.template.block_type}">{block.template.content}</div>'
                block_soup = BeautifulSoup(block_html, 'html.parser')
                paragraphs[block.position].insert_after(block_soup)
        
        return str(soup)
    
    @staticmethod
    def get_rendered_ctas(blog: BlogPost, context: Optional[Dict] = None) -> List[Dict]:
        """
        Get all active CTAs for a blog with rendered HTML.
        
        Args:
            blog: BlogPost instance
            context: Optional context for rendering
        
        Returns:
            List of CTA dictionaries with rendered HTML
        """
        placements = BlogCTAPlacement.objects.filter(
            blog=blog,
            is_active=True,
            cta_block__is_active=True
        ).select_related('cta_block').order_by('position')
        
        rendered_ctas = []
        for placement in placements:
            cta = placement.cta_block
            cta_data = {
                'id': cta.id,
                'placement_id': placement.id,  # Include placement ID for tracking
                'type': cta.cta_type,
                'title': cta.title,
                'description': cta.description,
                'button_text': cta.button_text,
                'button_url': cta.button_url,
                'style': cta.style,
                'placement_type': placement.placement_type,
                'position': placement.position,
                'tracking_id': cta.tracking_id or f"cta_{cta.id}",
                'image': cta.image.url if cta.image else None,
            }
            
            # Render HTML based on CTA type
            if cta.cta_type == 'custom':
                cta_data['html'] = cta.custom_html
            else:
                cta_data['html'] = ContentBlockService._render_cta_html(cta)
            
            rendered_ctas.append(cta_data)
        
        return rendered_ctas
    
    @staticmethod
    def _render_cta_html(cta: CTABlock) -> str:
        """Render HTML for a CTA block."""
        html = f'<div class="cta-block cta-{cta.cta_type} cta-{cta.style}">'
        
        if cta.title:
            html += f'<h3 class="cta-title">{cta.title}</h3>'
        
        if cta.description:
            html += f'<p class="cta-description">{cta.description}</p>'
        
        if cta.button_text and cta.button_url:
            html += f'<a href="{cta.button_url}" class="cta-button" data-tracking-id="{cta.tracking_id or cta.id}">{cta.button_text}</a>'
        
        if cta.image:
            html += f'<img src="{cta.image.url}" alt="{cta.title}" class="cta-image">'
        
        html += '</div>'
        return html

