"""
Content Health Check Service - Real-time validation for editor.
"""
from typing import Dict, List, Optional
from django.utils.html import strip_tags
import re


class ContentHealthService:
    """
    Service for real-time content health checks during editing.
    Provides SEO, readability, and content quality feedback.
    """
    
    @staticmethod
    def check_meta_title(title: Optional[str]) -> Dict:
        """
        Check meta title health.
        Returns: { valid: bool, score: int, issues: List[str], suggestions: List[str] }
        """
        if not title:
            return {
                'valid': False,
                'score': 0,
                'issues': ['missing_meta_title'],
                'suggestions': ['Add a meta title for better SEO'],
                'length': 0,
                'optimal_length': 50
            }
        
        length = len(title)
        issues = []
        suggestions = []
        score = 100
        
        # Length checks
        if length > 60:
            issues.append('meta_title_too_long')
            suggestions.append(f'Meta title is {length} characters. Recommended: 50-60 characters.')
            score -= 30
        elif length < 30:
            issues.append('meta_title_too_short')
            suggestions.append('Meta title is too short. Aim for 50-60 characters for better SEO.')
            score -= 20
        elif length < 50:
            suggestions.append('Meta title could be longer (50-60 characters is optimal).')
            score -= 10
        
        # Content checks
        if title.lower().startswith('home') or title.lower().startswith('page'):
            issues.append('generic_title')
            suggestions.append('Avoid generic titles. Be specific and descriptive.')
            score -= 15
        
        # Check for keywords (basic)
        if len(title.split()) < 3:
            issues.append('too_few_words')
            suggestions.append('Include more descriptive words in your title.')
            score -= 10
        
        return {
            'valid': len(issues) == 0,
            'score': max(0, score),
            'issues': issues,
            'suggestions': suggestions,
            'length': length,
            'optimal_length': 50
        }
    
    @staticmethod
    def check_meta_description(description: Optional[str]) -> Dict:
        """
        Check meta description health.
        """
        if not description:
            return {
                'valid': False,
                'score': 0,
                'issues': ['missing_meta_description'],
                'suggestions': ['Add a meta description for better SEO'],
                'length': 0,
                'optimal_length': 155
            }
        
        length = len(description)
        issues = []
        suggestions = []
        score = 100
        
        # Length checks
        if length > 160:
            issues.append('meta_description_too_long')
            suggestions.append(f'Meta description is {length} characters. Recommended: 150-160 characters.')
            score -= 30
        elif length < 120:
            issues.append('meta_description_too_short')
            suggestions.append('Meta description is too short. Aim for 150-160 characters.')
            score -= 20
        elif length < 150:
            suggestions.append('Meta description could be longer (150-160 characters is optimal).')
            score -= 10
        
        # Content checks
        if len(description.split()) < 15:
            issues.append('too_few_words')
            suggestions.append('Include more descriptive words in your meta description.')
            score -= 10
        
        # Check for call-to-action
        cta_words = ['learn', 'discover', 'explore', 'get', 'find', 'start', 'try']
        has_cta = any(word in description.lower() for word in cta_words)
        if not has_cta:
            suggestions.append('Consider adding a call-to-action word (learn, discover, explore, etc.).')
        
        return {
            'valid': len(issues) == 0,
            'score': max(0, score),
            'issues': issues,
            'suggestions': suggestions,
            'length': length,
            'optimal_length': 155
        }
    
    @staticmethod
    def check_content_quality(content: Optional[str], min_words: int = 300) -> Dict:
        """
        Check content quality (word count, readability, structure).
        """
        if not content:
            return {
                'valid': False,
                'score': 0,
                'issues': ['empty_content'],
                'suggestions': ['Add content to your post'],
                'word_count': 0,
                'min_words': min_words
            }
        
        # Strip HTML and count words
        text_content = strip_tags(content)
        words = text_content.split()
        word_count = len(words)
        
        issues = []
        suggestions = []
        score = 100
        
        # Word count checks
        if word_count < min_words:
            issues.append('low_word_count')
            suggestions.append(f'Content has {word_count} words. Recommended minimum: {min_words} words.')
            score -= 40
        elif word_count < min_words * 1.5:
            suggestions.append(f'Content has {word_count} words. Consider adding more detail (target: {min_words * 2} words).')
            score -= 10
        
        # Structure checks
        paragraphs = [p.strip() for p in text_content.split('\n\n') if p.strip()]
        if len(paragraphs) < 3:
            issues.append('insufficient_paragraphs')
            suggestions.append('Break content into more paragraphs for better readability.')
            score -= 15
        
        # Heading checks (basic - check for h2/h3 in HTML)
        heading_count = len(re.findall(r'<h[2-6]', content, re.IGNORECASE))
        if heading_count == 0 and word_count > 500:
            issues.append('no_headings')
            suggestions.append('Add headings (H2, H3) to improve readability and SEO.')
            score -= 20
        elif heading_count < 2 and word_count > 1000:
            suggestions.append('Consider adding more headings to break up long content.')
            score -= 10
        
        # Image checks
        image_count = len(re.findall(r'<img', content, re.IGNORECASE))
        if image_count == 0 and word_count > 800:
            suggestions.append('Consider adding images to break up long text.')
            score -= 5
        
        # Link checks
        link_count = len(re.findall(r'<a\s+href', content, re.IGNORECASE))
        if link_count == 0 and word_count > 500:
            suggestions.append('Consider adding internal or external links for better SEO.')
            score -= 5
        
        return {
            'valid': len(issues) == 0,
            'score': max(0, score),
            'issues': issues,
            'suggestions': suggestions,
            'word_count': word_count,
            'min_words': min_words,
            'paragraph_count': len(paragraphs),
            'heading_count': heading_count,
            'image_count': image_count,
            'link_count': link_count
        }
    
    @staticmethod
    def check_slug(slug: Optional[str]) -> Dict:
        """
        Check slug health.
        """
        if not slug:
            return {
                'valid': False,
                'score': 0,
                'issues': ['missing_slug'],
                'suggestions': ['Add a URL-friendly slug'],
                'length': 0
            }
        
        length = len(slug)
        issues = []
        suggestions = []
        score = 100
        
        # Length checks
        if length > 100:
            issues.append('slug_too_long')
            suggestions.append('Slug is too long. Keep it under 100 characters.')
            score -= 30
        elif length < 5:
            issues.append('slug_too_short')
            suggestions.append('Slug is too short. Make it more descriptive.')
            score -= 20
        
        # Format checks
        if not re.match(r'^[a-z0-9-]+$', slug):
            issues.append('invalid_slug_format')
            suggestions.append('Slug should only contain lowercase letters, numbers, and hyphens.')
            score -= 50
        
        # Check for stop words
        stop_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for']
        slug_words = slug.split('-')
        if any(word in stop_words for word in slug_words):
            suggestions.append('Consider removing common words (the, a, an, etc.) from slug.')
            score -= 5
        
        return {
            'valid': len(issues) == 0,
            'score': max(0, score),
            'issues': issues,
            'suggestions': suggestions,
            'length': length
        }
    
    @staticmethod
    def check_full_content(
        title: Optional[str] = None,
        meta_title: Optional[str] = None,
        meta_description: Optional[str] = None,
        content: Optional[str] = None,
        slug: Optional[str] = None,
        min_words: int = 300
    ) -> Dict:
        """
        Perform comprehensive content health check.
        Returns overall score and all individual checks.
        """
        checks = {
            'meta_title': ContentHealthService.check_meta_title(meta_title),
            'meta_description': ContentHealthService.check_meta_description(meta_description),
            'content': ContentHealthService.check_content_quality(content, min_words),
            'slug': ContentHealthService.check_slug(slug)
        }
        
        # Calculate overall score (weighted)
        scores = {
            'meta_title': checks['meta_title']['score'] * 0.2,
            'meta_description': checks['meta_description']['score'] * 0.2,
            'content': checks['content']['score'] * 0.5,
            'slug': checks['slug']['score'] * 0.1
        }
        
        overall_score = sum(scores.values())
        all_issues = []
        all_suggestions = []
        
        for check_name, check_result in checks.items():
            all_issues.extend([f"{check_name}:{issue}" for issue in check_result.get('issues', [])])
            all_suggestions.extend(check_result.get('suggestions', []))
        
        return {
            'overall_score': round(overall_score, 1),
            'overall_valid': len(all_issues) == 0,
            'checks': checks,
            'all_issues': all_issues,
            'all_suggestions': all_suggestions[:10],  # Limit to top 10
            'critical_issues': [issue for issue in all_issues if 'missing' in issue or 'invalid' in issue]
        }

