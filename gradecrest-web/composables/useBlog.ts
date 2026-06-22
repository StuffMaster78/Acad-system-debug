export interface GcStaticPost {
  slug: string
  title: string
  excerpt: string
  category: string
  readTime: string
  date: string
  author: string
  authorCredentials: string
}

const POSTS: GcStaticPost[] = [
  {
    slug: 'how-to-write-an-analytical-essay',
    title: 'How to Write an Analytical Essay: A Step-by-Step Guide',
    excerpt: 'An analytical essay goes beyond summarising — it asks you to examine evidence, evaluate arguments, and build a clear interpretive claim. This guide walks you through every stage, from picking a thesis to polishing your conclusion.',
    category: 'Essay Writing',
    readTime: '9 min read',
    date: '2025-03-12',
    author: 'Dr. Patricia Monroe',
    authorCredentials: 'PhD English Literature, University of Edinburgh',
  },
  {
    slug: 'how-to-write-a-research-paper-fast',
    title: 'How to Write a Research Paper Fast (Without Sacrificing Quality)',
    excerpt: 'Staring at a blank page with a deadline tomorrow? This tactical guide shows you how to plan, research, draft, and revise a research paper quickly — without cutting corners on quality or citations.',
    category: 'Research Papers',
    readTime: '11 min read',
    date: '2025-04-02',
    author: 'James Okafor',
    authorCredentials: 'MA Academic Writing, University of Leeds',
  },
  {
    slug: 'apa-7th-edition-citation-guide',
    title: 'APA 7th Edition: The Complete Citation Guide for 2025',
    excerpt: 'APA 7th edition brought significant changes to author rules, DOI formatting, and reference list style. This comprehensive guide covers every source type with real examples you can copy directly.',
    category: 'Citation & Format',
    readTime: '14 min read',
    date: '2025-05-18',
    author: 'Sarah Kimani',
    authorCredentials: 'MA Library & Information Science',
  },
]

export function useBlog() {
  function getAll()              { return POSTS }
  function getBySlug(slug: string) { return POSTS.find(p => p.slug === slug) ?? null }
  return { getAll, getBySlug }
}
