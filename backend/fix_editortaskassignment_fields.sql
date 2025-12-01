-- Fix for EditorTaskAssignment missing fields
-- Run with: docker-compose exec -T db psql -U postgres -d writingsondo < fix_editortaskassignment_fields.sql

ALTER TABLE editor_management_editortaskassignment
ADD COLUMN IF NOT EXISTS assignment_type VARCHAR(20) DEFAULT 'auto',
ADD COLUMN IF NOT EXISTS assigned_by_id BIGINT REFERENCES users_user(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS review_status VARCHAR(20) DEFAULT 'pending',
ADD COLUMN IF NOT EXISTS started_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS notes TEXT,
ADD COLUMN IF NOT EXISTS editor_rating INTEGER;

-- Create indexes
CREATE INDEX IF NOT EXISTS editor_management_editortaskassignment_assigned_editor_id_review_status_idx 
    ON editor_management_editortaskassignment(assigned_editor_id, review_status);
CREATE INDEX IF NOT EXISTS editor_management_editortaskassignment_review_status_assigned_at_idx 
    ON editor_management_editortaskassignment(review_status, assigned_at);
CREATE INDEX IF NOT EXISTS editor_management_editortaskassignment_order_id_idx 
    ON editor_management_editortaskassignment(order_id);

