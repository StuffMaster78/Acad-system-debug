-- Manual SQL to add content column to BlogPost table
-- Run this if the migration fails

-- For PostgreSQL
ALTER TABLE blog_pages_management_blogpost 
ADD COLUMN IF NOT EXISTS content TEXT;

-- Verify the column was added
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'blog_pages_management_blogpost' 
AND column_name = 'content';

