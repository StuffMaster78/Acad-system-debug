-- SQL script to manually add all missing columns and tables
-- Run this if migrations aren't working

-- ========================================
-- ORDERS: Add missing columns
-- ========================================
ALTER TABLE orders_order 
ADD COLUMN IF NOT EXISTS submitted_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS requires_editing BOOLEAN DEFAULT NULL,
ADD COLUMN IF NOT EXISTS editing_skip_reason VARCHAR(255);

-- ========================================
-- COMMUNICATIONS: Add missing columns
-- ========================================
ALTER TABLE communications_communicationthread
ADD COLUMN IF NOT EXISTS content_type_id INTEGER REFERENCES django_content_type(id) ON DELETE CASCADE,
ADD COLUMN IF NOT EXISTS object_id INTEGER;

-- ========================================
-- BLOG PAGES: Add BlogCategory missing columns
-- ========================================
ALTER TABLE blog_pages_management_blogcategory
ADD COLUMN IF NOT EXISTS meta_title VARCHAR(255),
ADD COLUMN IF NOT EXISTS meta_description TEXT,
ADD COLUMN IF NOT EXISTS category_image VARCHAR(100),
ADD COLUMN IF NOT EXISTS post_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS total_views INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS total_conversions INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS display_order INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS is_featured BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- ========================================
-- BLOG PAGES: Add BlogPost content column
-- ========================================
ALTER TABLE blog_pages_management_blogpost
ADD COLUMN IF NOT EXISTS content TEXT,
ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'draft';

-- ========================================
-- BLOG PAGES: Create PDF Sample tables
-- ========================================

-- PDFSampleSection
CREATE TABLE IF NOT EXISTS blog_pages_management_pdfsamplesection (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    requires_auth BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    blog_id BIGINT NOT NULL REFERENCES blog_pages_management_blogpost(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS blog_pages_management_pdfsamplesection_blog_id_is_active_idx 
ON blog_pages_management_pdfsamplesection(blog_id, is_active);

-- PDFSample
CREATE TABLE IF NOT EXISTS blog_pages_management_pdfsample (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    pdf_file VARCHAR(100) NOT NULL,
    file_size INTEGER,
    display_order INTEGER DEFAULT 0,
    download_count INTEGER DEFAULT 0,
    is_featured BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    section_id BIGINT NOT NULL REFERENCES blog_pages_management_pdfsamplesection(id) ON DELETE CASCADE,
    uploaded_by_id BIGINT REFERENCES users_user(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS blog_pages_management_pdfsample_section_id_is_active_idx 
ON blog_pages_management_pdfsample(section_id, is_active);
CREATE INDEX IF NOT EXISTS blog_pages_management_pdfsample_download_count_idx 
ON blog_pages_management_pdfsample(download_count);

-- PDFSampleDownload
CREATE TABLE IF NOT EXISTS blog_pages_management_pdfsampledownload (
    id BIGSERIAL PRIMARY KEY,
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(255),
    downloaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    pdf_sample_id BIGINT NOT NULL REFERENCES blog_pages_management_pdfsample(id) ON DELETE CASCADE,
    user_id BIGINT REFERENCES users_user(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS blog_pages_management_pdfsampledownload_pdf_sample_id_downloaded_at_idx 
ON blog_pages_management_pdfsampledownload(pdf_sample_id, downloaded_at);
CREATE INDEX IF NOT EXISTS blog_pages_management_pdfsampledownload_user_id_downloaded_at_idx 
ON blog_pages_management_pdfsampledownload(user_id, downloaded_at);

-- ========================================
-- Verify changes
-- ========================================
SELECT 'Orders columns' as check_type, 
       COUNT(*) as missing_columns
FROM information_schema.columns 
WHERE table_name = 'orders_order' 
AND column_name IN ('submitted_at', 'requires_editing', 'editing_skip_reason')
HAVING COUNT(*) < 3

UNION ALL

SELECT 'Communications columns' as check_type,
       COUNT(*) as missing_columns
FROM information_schema.columns
WHERE table_name = 'communications_communicationthread'
AND column_name IN ('content_type_id', 'object_id')
HAVING COUNT(*) < 2

UNION ALL

SELECT 'BlogCategory columns' as check_type,
       COUNT(*) as missing_columns
FROM information_schema.columns
WHERE table_name = 'blog_pages_management_blogcategory'
AND column_name IN ('meta_title', 'created_at')
HAVING COUNT(*) < 2

UNION ALL

SELECT 'BlogPost content' as check_type,
       CASE WHEN EXISTS (
           SELECT 1 FROM information_schema.columns
           WHERE table_name = 'blog_pages_management_blogpost'
           AND column_name = 'content'
       ) THEN 0 ELSE 1 END as missing_columns

UNION ALL

SELECT 'PDFSampleSection table' as check_type,
       CASE WHEN EXISTS (
           SELECT 1 FROM information_schema.tables
           WHERE table_name = 'blog_pages_management_pdfsamplesection'
       ) THEN 0 ELSE 1 END as missing_columns;

