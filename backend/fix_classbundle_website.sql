-- Quick fix to add all missing columns to ClassBundle table
-- Run with: docker-compose exec -T db psql -U postgres -d writingsondo < fix_classbundle_website.sql

ALTER TABLE class_management_classbundle
ADD COLUMN IF NOT EXISTS website_id BIGINT REFERENCES websites_website(id) ON DELETE CASCADE,
ADD COLUMN IF NOT EXISTS assigned_writer_id BIGINT REFERENCES users_user(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS pricing_source VARCHAR(20) DEFAULT 'config',
ADD COLUMN IF NOT EXISTS start_date DATE,
ADD COLUMN IF NOT EXISTS end_date DATE,
ADD COLUMN IF NOT EXISTS deposit_required NUMERIC(10, 2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS deposit_paid NUMERIC(10, 2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS installments_enabled BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS installment_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS original_price NUMERIC(10, 2),
ADD COLUMN IF NOT EXISTS discount_id BIGINT REFERENCES discounts_discount(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS created_by_admin_id BIGINT REFERENCES users_user(id) ON DELETE SET NULL;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS class_management_classbundle_website_id_idx 
    ON class_management_classbundle(website_id);
CREATE INDEX IF NOT EXISTS class_management_classbundle_assigned_writer_id_idx 
    ON class_management_classbundle(assigned_writer_id);
CREATE INDEX IF NOT EXISTS class_management_classbundle_discount_id_idx 
    ON class_management_classbundle(discount_id);
CREATE INDEX IF NOT EXISTS class_management_classbundle_created_by_admin_id_idx 
    ON class_management_classbundle(created_by_admin_id);

