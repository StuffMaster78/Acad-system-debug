"""
Management command to seed blogs, SEO pages, authors, tags, and categories with fake data.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from websites.models import Website
from blog_pages_management.models import (
    AuthorProfile, BlogCategory, BlogTag, BlogPost, BlogFAQ,
    BlogSEOMetadata, FAQSchema
)
from seo_pages.models import SeoPage
from datetime import timedelta
import random
from faker import Faker

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = 'Seed blogs, SEO pages, authors, tags, and categories with fake data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--blogs',
            type=int,
            default=50,
            help='Number of blog posts to create (default: 50)'
        )
        parser.add_argument(
            '--seo-pages',
            type=int,
            default=20,
            help='Number of SEO pages to create (default: 20)'
        )
        parser.add_argument(
            '--authors',
            type=int,
            default=10,
            help='Number of authors to create (default: 10)'
        )
        parser.add_argument(
            '--categories',
            type=int,
            default=8,
            help='Number of categories to create (default: 8)'
        )
        parser.add_argument(
            '--tags',
            type=int,
            default=30,
            help='Number of tags to create (default: 30)'
        )

    def handle(self, *args, **options):
        blogs_count = options['blogs']
        seo_pages_count = options['seo_pages']
        authors_count = options['authors']
        categories_count = options['categories']
        tags_count = options['tags']

        self.stdout.write(self.style.SUCCESS('Starting to seed blog and SEO data...'))

        # Get websites
        websites = list(Website.objects.all())
        if not websites:
            self.stdout.write(self.style.ERROR('No websites found. Please create websites first.'))
            return

        # Get admin users for created_by fields
        admin_users = list(User.objects.filter(is_staff=True)[:5])
        if not admin_users:
            admin_users = list(User.objects.all()[:5])

        # Create authors
        self.stdout.write('Creating authors...')
        authors = self.create_authors(websites, authors_count)
        self.stdout.write(self.style.SUCCESS(f'Created {len(authors)} authors'))

        # Create categories
        self.stdout.write('Creating categories...')
        categories = self.create_categories(websites, categories_count)
        self.stdout.write(self.style.SUCCESS(f'Created {len(categories)} categories'))

        # Create tags
        self.stdout.write('Creating tags...')
        tags = self.create_tags(websites, tags_count)
        self.stdout.write(self.style.SUCCESS(f'Created {len(tags)} tags'))

        # Create blog posts
        self.stdout.write('Creating blog posts...')
        blog_posts = self.create_blog_posts(
            websites, authors, categories, tags, admin_users, blogs_count
        )
        self.stdout.write(self.style.SUCCESS(f'Created {len(blog_posts)} blog posts'))

        # Create SEO pages
        self.stdout.write('Creating SEO pages...')
        seo_pages = self.create_seo_pages(websites, admin_users, seo_pages_count)
        self.stdout.write(self.style.SUCCESS(f'Created {len(seo_pages)} SEO pages'))

        self.stdout.write(self.style.SUCCESS('\n✅ Successfully seeded all blog and SEO data!'))
        self.stdout.write(f'   - Authors: {len(authors)}')
        self.stdout.write(f'   - Categories: {len(categories)}')
        self.stdout.write(f'   - Tags: {len(tags)}')
        self.stdout.write(f'   - Blog Posts: {len(blog_posts)}')
        self.stdout.write(f'   - SEO Pages: {len(seo_pages)}')

    def create_authors(self, websites, count):
        """Create author profiles."""
        authors = []
        designations = [
            'Senior Content Writer', 'Content Strategist', 'SEO Specialist',
            'Technical Writer', 'Copywriter', 'Content Manager',
            'Blog Editor', 'Content Creator', 'Digital Marketing Writer'
        ]
        expertise_areas = [
            'Academic Writing', 'Business Writing', 'Technical Writing',
            'Creative Writing', 'SEO Content', 'Marketing Content',
            'Research Writing', 'Copywriting', 'Content Strategy'
        ]

        for i in range(count):
            website = random.choice(websites)
            name = fake.name()
            
            # Ensure unique name
            while AuthorProfile.objects.filter(name=name).exists():
                name = fake.name()

            author = AuthorProfile.objects.create(
                website=website,
                name=name,
                bio=fake.text(max_nb_chars=300),
                designation=random.choice(designations),
                expertise=random.choice(expertise_areas),
                contact_email=fake.email(),
                twitter_handle=f"@{fake.user_name()}" if random.random() > 0.5 else None,
                linkedin_profile=f"https://linkedin.com/in/{fake.user_name()}" if random.random() > 0.5 else None,
                social_links={
                    'twitter': f"https://twitter.com/{fake.user_name()}" if random.random() > 0.5 else None,
                    'linkedin': f"https://linkedin.com/in/{fake.user_name()}" if random.random() > 0.5 else None,
                },
                is_fake=True
            )
            authors.append(author)
        return authors

    def create_categories(self, websites, count):
        """Create blog categories."""
        categories = []
        category_names = [
            'Academic Writing', 'Business Tips', 'Career Advice',
            'Study Guides', 'Writing Tips', 'Research Methods',
            'Essay Writing', 'Assignment Help', 'Student Resources',
            'Professional Development', 'Industry Insights', 'Best Practices'
        ]

        for i in range(count):
            website = random.choice(websites)
            name = random.choice(category_names)
            
            # Ensure unique slug per website
            base_slug = slugify(name)
            slug = base_slug
            counter = 1
            while BlogCategory.objects.filter(website=website, slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            category = BlogCategory.objects.create(
                website=website,
                name=name,
                description=fake.text(max_nb_chars=200),
                slug=slug,
                meta_title=f"{name} - Expert Guides and Tips",
                meta_description=fake.text(max_nb_chars=160),
                post_count=0,
                display_order=i,
                is_featured=random.random() > 0.7,
                is_active=True
            )
            categories.append(category)
        return categories

    def create_tags(self, websites, count):
        """Create blog tags."""
        tags = []
        tag_names = [
            'essay writing', 'academic help', 'study tips', 'research',
            'citation', 'plagiarism', 'grammar', 'writing style',
            'dissertation', 'thesis', 'assignment', 'homework',
            'academic success', 'student life', 'college tips',
            'professional writing', 'business writing', 'technical writing',
            'creative writing', 'content marketing', 'SEO', 'blogging',
            'writing skills', 'editing', 'proofreading', 'formatting',
            'APA style', 'MLA style', 'Chicago style', 'Harvard style'
        ]

        created_names = set()
        for i in range(count):
            website = random.choice(websites)
            name = random.choice(tag_names)
            
            # Ensure unique name
            while name in created_names or BlogTag.objects.filter(name=name).exists():
                name = random.choice(tag_names)
            
            created_names.add(name)
            tag = BlogTag.objects.create(
                website=website,
                name=name
            )
            tags.append(tag)
        return tags

    def create_blog_posts(self, websites, authors, categories, tags, admin_users, count):
        """Create blog posts with various statuses."""
        blog_posts = []
        statuses = ['draft', 'scheduled', 'published', 'archived']
        status_weights = [0.2, 0.1, 0.6, 0.1]  # More published posts

        # First, create all blogs as drafts to build up a pool for internal links
        draft_blogs = []
        for i in range(count):
            website = random.choice(websites)
            status = 'draft'  # Start as draft
            
            # Generate title and slug
            title = fake.sentence(nb_words=6).rstrip('.')
            base_slug = slugify(title)
            slug = base_slug
            counter = 1
            while BlogPost.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            # Create content with headings
            content = self.generate_blog_content()

            # Select random authors, category, and tags
            selected_authors = random.sample(authors, min(random.randint(1, 3), len(authors)))
            category = random.choice(categories) if categories else None
            selected_tags = random.sample(tags, min(random.randint(2, 5), len(tags)))

            blog = BlogPost.objects.create(
                website=website,
                title=title,
                slug=slug,
                content=content,
                meta_title=f"{title} | Expert Guide"[:60],
                meta_description=fake.text(max_nb_chars=160),
                status=status,
                is_published=False,
                publish_date=None,
                category=category,
                is_featured=random.random() > 0.85,
                is_editorial=random.random() > 0.7,
                click_count=0,
                conversion_count=0,
            )

            # Add many-to-many relationships
            blog.authors.set(selected_authors)
            blog.tags.set(selected_tags)

            draft_blogs.append(blog)
            blog_posts.append(blog)

        # Now update some to published/scheduled with internal links
        published_count = int(count * 0.6)
        scheduled_count = int(count * 0.1)
        
        # Get all blog slugs for internal linking
        all_blog_slugs = [b.slug for b in draft_blogs]
        
        for i, blog in enumerate(draft_blogs):
            if i < published_count:
                # Make it published
                status = 'published'
                publish_date = timezone.now() - timedelta(days=random.randint(1, 180))
                # Add internal links to content
                content_with_links = self.add_internal_links(blog.content, all_blog_slugs, blog.slug)
                blog.content = content_with_links
                blog.status = status
                blog.is_published = True
                blog.publish_date = publish_date
                blog.click_count = random.randint(0, 1000)
                blog.conversion_count = random.randint(0, 50)
                blog.save()
                
                # Create SEO metadata
                self.create_seo_metadata_for_blog(blog, list(blog.authors.all()))
            elif i < published_count + scheduled_count:
                # Make it scheduled
                status = 'scheduled'
                publish_date = timezone.now() + timedelta(days=random.randint(1, 30))
                # Add internal links to content
                content_with_links = self.add_internal_links(blog.content, all_blog_slugs, blog.slug)
                blog.content = content_with_links
                blog.status = status
                blog.scheduled_publish_date = publish_date
                blog.save()
            # Others remain as drafts

            # Create FAQs for some blogs
            if random.random() > 0.6:
                self.create_faqs_for_blog(blog, blog.website)

        return blog_posts

    def generate_blog_content(self):
        """Generate realistic blog content with headings."""
        content_parts = [
            f"<h2>{fake.sentence(nb_words=4).rstrip('.')}</h2>",
            f"<p>{fake.paragraph(nb_sentences=5)}</p>",
            f"<h3>{fake.sentence(nb_words=4).rstrip('.')}</h3>",
            f"<p>{fake.paragraph(nb_sentences=4)}</p>",
            f"<ul>",
            f"<li>{fake.sentence()}</li>",
            f"<li>{fake.sentence()}</li>",
            f"<li>{fake.sentence()}</li>",
            f"</ul>",
            f"<h2>{fake.sentence(nb_words=4).rstrip('.')}</h2>",
            f"<p>{fake.paragraph(nb_sentences=6)}</p>",
            f"<h3>{fake.sentence(nb_words=4).rstrip('.')}</h3>",
            f"<p>{fake.paragraph(nb_sentences=4)}</p>",
            f"<h2>Conclusion</h2>",
            f"<p>{fake.paragraph(nb_sentences=4)}</p>",
        ]
        return "\n".join(content_parts)

    def add_internal_links(self, content, all_slugs, current_slug):
        """Add internal links to blog content."""
        # Get 5-7 random slugs (excluding current)
        available_slugs = [s for s in all_slugs if s != current_slug]
        if len(available_slugs) < 5:
            # If not enough other blogs, just return content as-is
            return content
        
        link_slugs = random.sample(available_slugs, min(random.randint(5, 7), len(available_slugs)))
        
        # Add links at various points in the content
        paragraphs = content.split('</p>')
        link_count = 0
        result_parts = []
        
        for i, para in enumerate(paragraphs):
            result_parts.append(para)
            if para.strip() and '</p>' not in para and link_count < len(link_slugs):
                # Add a link after this paragraph
                link_text = fake.sentence(nb_words=3).rstrip('.')
                link_slug = link_slugs[link_count]
                result_parts.append(f' <a href="/{link_slug}">{link_text}</a>')
                link_count += 1
            if i < len(paragraphs) - 1:
                result_parts.append('</p>')
        
        return ''.join(result_parts)

    def create_faqs_for_blog(self, blog, website):
        """Create FAQs for a blog post."""
        faq_count = random.randint(3, 6)
        questions = [
            "What is the main purpose of this guide?",
            "How can I apply these tips in my work?",
            "What are the key takeaways?",
            "Are there any prerequisites?",
            "How long does it take to see results?",
            "What resources do I need?",
        ]

        for i in range(faq_count):
            question = random.choice(questions)
            BlogFAQ.objects.create(
                website=website,
                blog=blog,
                question=question,
                answer=fake.paragraph(nb_sentences=3)
            )

    def create_seo_metadata_for_blog(self, blog, authors):
        """Create SEO metadata for a blog post."""
        try:
            article_section = (blog.category.name if blog.category else 'General')[:50]  # Truncate to 50 chars
            BlogSEOMetadata.objects.create(
                blog=blog,
                article_type='BlogPosting',
                article_section=article_section,
                keywords=', '.join([tag.name for tag in blog.tags.all()[:5]])[:500],  # Truncate to 500 chars
                article_published_time=blog.publish_date or timezone.now(),
                article_modified_time=timezone.now(),
                article_author_url=f"https://example.com/authors/{authors[0].name.lower().replace(' ', '-')}" if authors else '',
                og_type='article',
                og_title=(blog.meta_title or blog.title)[:255],  # Ensure within limit
                og_description=(blog.meta_description or fake.text(max_nb_chars=200))[:500],  # Truncate if needed
            )
        except Exception as e:
            # If SEO metadata already exists, skip
            pass

    def create_seo_pages(self, websites, admin_users, count):
        """Create SEO pages."""
        seo_pages = []
        page_titles = [
            'Best Essay Writing Service',
            'Professional Assignment Help',
            'Expert Dissertation Writing',
            'Top Academic Writing Services',
            'Reliable Homework Help',
            'Quality Research Paper Writing',
            'Affordable Essay Writing',
            'Custom Paper Writing Service',
            'Online Writing Assistance',
            'Professional Writing Help',
            'Academic Writing Experts',
            'Essay Writing Guide',
            'How to Write Better Essays',
            'Academic Writing Tips',
            'Professional Writing Services',
            'Essay Writing Help Online',
            'Custom Essay Writing',
            'Quality Writing Services',
            'Expert Writing Assistance',
            'Professional Academic Help',
        ]

        for i in range(count):
            website = random.choice(websites)
            title = random.choice(page_titles)
            
            # Ensure unique slug per website
            base_slug = slugify(title)
            slug = base_slug
            counter = 1
            while SeoPage.objects.filter(website=website, slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            # Random publish status
            is_published = random.random() > 0.3
            publish_date = timezone.now() - timedelta(days=random.randint(1, 90)) if is_published else None

            # Generate content blocks
            blocks = self.generate_seo_page_blocks()

            seo_page = SeoPage.objects.create(
                website=website,
                title=title,
                slug=slug,
                meta_title=f"{title} | Expert Guide & Reviews",
                meta_description=fake.text(max_nb_chars=160),
                blocks=blocks,
                is_published=is_published,
                publish_date=publish_date,
                created_by=random.choice(admin_users) if admin_users else None,
                updated_by=random.choice(admin_users) if admin_users else None,
            )
            seo_pages.append(seo_page)

        return seo_pages

    def generate_seo_page_blocks(self):
        """Generate content blocks for SEO pages."""
        blocks = [
            {
                'type': 'heading',
                'level': 1,
                'content': fake.sentence(nb_words=6).rstrip('.')
            },
            {
                'type': 'paragraph',
                'content': fake.paragraph(nb_sentences=4)
            },
            {
                'type': 'heading',
                'level': 2,
                'content': fake.sentence(nb_words=5).rstrip('.')
            },
            {
                'type': 'paragraph',
                'content': fake.paragraph(nb_sentences=5)
            },
            {
                'type': 'list',
                'style': 'unordered',
                'items': [
                    fake.sentence(),
                    fake.sentence(),
                    fake.sentence(),
                ]
            },
            {
                'type': 'heading',
                'level': 2,
                'content': fake.sentence(nb_words=5).rstrip('.')
            },
            {
                'type': 'paragraph',
                'content': fake.paragraph(nb_sentences=4)
            },
            {
                'type': 'cta',
                'text': 'Get Started Today',
                'link': '/orders/new',
                'style': 'primary'
            }
        ]
        return blocks

