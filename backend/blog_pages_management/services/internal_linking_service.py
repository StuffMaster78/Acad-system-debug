"""
Service for internal linking recommendations and content suggestions.
Provides intelligent suggestions for linking between blog posts, SEO pages, and related content.
"""
import logging
from typing import List, Dict, Optional
from django.db.models import Q, Count
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)


class InternalLinkingService:
    """
    Service for generating internal linking recommendations based on:
    - Content similarity (tags, categories, keywords)
    - Semantic similarity (embeddings if available)
    - User engagement patterns
    - SEO relevance
    """

    @staticmethod
    def suggest_internal_links(
        content: str,
        website_id: int,
        current_post_id: Optional[int] = None,
        limit: int = 10,
        content_type: str = 'blog'  # 'blog' or 'seo_page'
    ) -> List[Dict]:
        """
        Suggest internal links based on content analysis.
        
        Args:
            content: The content text to analyze
            website_id: Website ID to filter suggestions
            current_post_id: ID of current post to exclude from suggestions
            limit: Maximum number of suggestions
            content_type: Type of content ('blog' or 'seo_page')
        
        Returns:
            List of suggested posts/pages with relevance scores
        """
        from blog_pages_management.models import BlogPost
        try:
            from service_pages_management._legacy_models import ServicePage
        except ImportError:
            ServicePage = None
        
        cache_key = f"internal_links:{website_id}:{current_post_id}:{hash(content[:200])}:{limit}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        suggestions = []
        
        # Extract keywords from content (simple approach - can be enhanced with NLP)
        keywords = InternalLinkingService._extract_keywords(content)
        
        if content_type == 'blog':
            # Get blog posts from same website
            queryset = BlogPost.objects.filter(
                website_id=website_id,
                is_published=True,
                is_deleted=False
            ).exclude(id=current_post_id) if current_post_id else BlogPost.objects.filter(
                website_id=website_id,
                is_published=True,
                is_deleted=False
            )
            
            # Score posts based on relevance
            for post in queryset.select_related('category', 'website')[:50]:  # Limit initial query
                score = InternalLinkingService._calculate_relevance_score(
                    post, keywords, content
                )
                if score > 0:
                    suggestions.append({
                        'id': post.id,
                        'title': post.title,
                        'slug': post.slug,
                        'url': f"/blog/{post.slug}/",
                        'category': post.category.name if post.category else None,
                        'score': score,
                        'type': 'blog',
                        'excerpt': post.meta_description or post.content[:150] + '...' if post.content else ''
                    })
        else:
            # Get SEO pages from same website
            if ServicePage is None:
                return []
            
            queryset = ServicePage.objects.filter(
                website_id=website_id,
                is_published=True,
                is_active=True
            ).exclude(id=current_post_id) if current_post_id else ServicePage.objects.filter(
                website_id=website_id,
                is_published=True,
                is_active=True
            )
            
            for page in queryset[:50]:
                score = InternalLinkingService._calculate_relevance_score(
                    page, keywords, content
                )
                if score > 0:
                    suggestions.append({
                        'id': page.id,
                        'title': page.title,
                        'slug': page.slug,
                        'url': f"/{page.slug}/",
                        'score': score,
                        'type': 'seo_page',
                        'excerpt': page.short_description or page.content[:150] + '...' if page.content else ''
                    })
        
        # Sort by score and return top results
        suggestions.sort(key=lambda x: x['score'], reverse=True)
        result = suggestions[:limit]
        
        # Cache for 1 hour
        cache.set(cache_key, result, timeout=3600)
        return result

    @staticmethod
    def get_related_content(
        post_id: int,
        website_id: int,
        content_type: str = 'blog',
        limit: int = 5
    ) -> List[Dict]:
        """
        Get related content for a specific post/page.
        
        Args:
            post_id: ID of the post/page
            website_id: Website ID
            content_type: 'blog' or 'seo_page'
            limit: Maximum number of related items
        
        Returns:
            List of related content items
        """
        from blog_pages_management.models import BlogPost
        try:
            from service_pages_management._legacy_models import ServicePage
        except ImportError:
            ServicePage = None
        
        cache_key = f"related_content:{content_type}:{post_id}:{limit}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        related = []
        
        try:
            if content_type == 'blog':
                post = BlogPost.objects.select_related('category', 'website').prefetch_related('tags').get(
                    id=post_id,
                    website_id=website_id
                )
                
                # Find related by tags
                if post.tags.exists():
                    tag_ids = post.tags.values_list('id', flat=True)
                    related_posts = BlogPost.objects.filter(
                        website_id=website_id,
                        is_published=True,
                        is_deleted=False,
                        tags__in=tag_ids
                    ).exclude(id=post_id).distinct().annotate(
                        tag_count=Count('tags')
                    ).order_by('-tag_count', '-click_count', '-publish_date')[:limit]
                    
                    for related_post in related_posts:
                        related.append({
                            'id': related_post.id,
                            'title': related_post.title,
                            'slug': related_post.slug,
                            'url': f"/blog/{related_post.slug}/",
                            'type': 'blog',
                            'category': related_post.category.name if related_post.category else None,
                            'excerpt': related_post.meta_description or related_post.content[:150] + '...' if related_post.content else '',
                            'publish_date': related_post.publish_date.isoformat() if related_post.publish_date else None
                        })
                
                # If not enough by tags, add by category
                if len(related) < limit and post.category:
                    category_posts = BlogPost.objects.filter(
                        website_id=website_id,
                        is_published=True,
                        is_deleted=False,
                        category=post.category
                    ).exclude(id=post_id).exclude(
                        id__in=[r['id'] for r in related]
                    ).order_by('-click_count', '-publish_date')[:limit - len(related)]
                    
                    for related_post in category_posts:
                        related.append({
                            'id': related_post.id,
                            'title': related_post.title,
                            'slug': related_post.slug,
                            'url': f"/blog/{related_post.slug}/",
                            'type': 'blog',
                            'category': related_post.category.name if related_post.category else None,
                            'excerpt': related_post.meta_description or related_post.content[:150] + '...' if related_post.content else '',
                            'publish_date': related_post.publish_date.isoformat() if related_post.publish_date else None
                        })
            else:
                if ServicePage is None:
                    return []
                
                page = ServicePage.objects.get(
                    id=post_id,
                    website_id=website_id
                )
                
                # Find related SEO pages by keywords in title/description
                related_pages = ServicePage.objects.filter(
                    website_id=website_id,
                    is_published=True,
                    is_active=True
                ).exclude(id=post_id).order_by('-click_count', '-updated_at')[:limit]
                
                for related_page in related_pages:
                    related.append({
                        'id': related_page.id,
                        'title': related_page.title,
                        'slug': related_page.slug,
                        'url': f"/{related_page.slug}/",
                        'type': 'seo_page',
                        'excerpt': related_page.short_description or page.content[:150] + '...' if related_page.content else ''
                    })
        
        except BlogPost.DoesNotExist:
            logger.warning(f"Blog post with id {post_id} not found")
            return []
        except Exception as e:
            if ServicePage and isinstance(e, ServicePage.DoesNotExist):
                logger.warning(f"SEO page with id {post_id} not found")
                return []
            raise
            logger.warning(f"{content_type} with id {post_id} not found")
            return []
        
        # Cache for 30 minutes
        cache.set(cache_key, related, timeout=1800)
        return related

    @staticmethod
    def _extract_keywords(content: str, max_keywords: int = 10) -> List[str]:
        """
        Extract keywords from content (simple word frequency approach).
        Can be enhanced with NLP libraries like spaCy or NLTK.
        """
        import re
        from collections import Counter
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', content)
        
        # Extract words (3+ characters, alphanumeric)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Common stop words to exclude
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her',
            'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how',
            'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy',
            'did', 'has', 'let', 'put', 'say', 'she', 'too', 'use', 'this', 'that',
            'with', 'from', 'have', 'will', 'your', 'what', 'when', 'where', 'which',
            'would', 'could', 'should', 'about', 'after', 'before', 'during', 'while'
        }
        
        # Filter stop words and count
        keywords = [w for w in words if w not in stop_words]
        word_freq = Counter(keywords)
        
        # Return top keywords
        return [word for word, _ in word_freq.most_common(max_keywords)]

    @staticmethod
    def _calculate_relevance_score(
        post_or_page,
        keywords: List[str],
        content: str
    ) -> float:
        """
        Calculate relevance score for a post/page based on keywords and content.
        
        Returns:
            Float score (0.0 to 1.0)
        """
        score = 0.0
        
        # Check title for keywords
        title_lower = post_or_page.title.lower()
        title_matches = sum(1 for kw in keywords if kw in title_lower)
        score += (title_matches / max(len(keywords), 1)) * 0.4
        
        # Check content/description for keywords
        content_text = ''
        if hasattr(post_or_page, 'content'):
            content_text = post_or_page.content or ''
        if hasattr(post_or_page, 'meta_description'):
            content_text += ' ' + (post_or_page.meta_description or '')
        if hasattr(post_or_page, 'short_description'):
            content_text += ' ' + (post_or_page.short_description or '')
        
        content_lower = content_text.lower()
        content_matches = sum(1 for kw in keywords if kw in content_lower)
        score += (content_matches / max(len(keywords), 1)) * 0.3
        
        # Boost score for popular content
        if hasattr(post_or_page, 'click_count') and post_or_page.click_count:
            # Normalize click count (assuming max 10000 clicks = 1.0)
            click_boost = min(post_or_page.click_count / 10000.0, 0.2)
            score += click_boost
        
        # Boost for recent content
        if hasattr(post_or_page, 'publish_date') and post_or_page.publish_date:
            days_old = (timezone.now() - post_or_page.publish_date).days
            if days_old < 30:
                recency_boost = (30 - days_old) / 30.0 * 0.1
                score += recency_boost
        
        return min(score, 1.0)

