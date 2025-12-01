-- Comprehensive fix for all missing EditorProfile, EditorPerformance, and EditorActionLog fields
-- Run with: docker-compose exec -T db psql -U postgres -d writingsondo < fix_all_editor_management_fields.sql

-- EditorProfile missing fields
ALTER TABLE editor_management_editorprofile
ADD COLUMN IF NOT EXISTS can_self_assign BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS max_concurrent_tasks INTEGER DEFAULT 5;

-- EditorPerformance missing fields
ALTER TABLE editor_management_editorperformance
ADD COLUMN IF NOT EXISTS average_review_time INTERVAL,
ADD COLUMN IF NOT EXISTS total_orders_reviewed INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS late_reviews INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS average_quality_score NUMERIC(3, 2),
ADD COLUMN IF NOT EXISTS revisions_requested_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS approvals_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS last_calculated_at TIMESTAMP WITH TIME ZONE;

-- EditorActionLog missing fields
-- Add with defaults first for existing records
ALTER TABLE editor_management_editoractionlog
ADD COLUMN IF NOT EXISTS action_type VARCHAR(50) DEFAULT 'completed_task',
ADD COLUMN IF NOT EXISTS action VARCHAR(255) DEFAULT 'Action performed',
ADD COLUMN IF NOT EXISTS related_order_id BIGINT REFERENCES orders_order(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS related_task_id BIGINT REFERENCES editor_management_editortaskassignment(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Remove defaults after adding (optional, to match model)
-- ALTER TABLE editor_management_editoractionlog ALTER COLUMN action_type DROP DEFAULT;
-- ALTER TABLE editor_management_editoractionlog ALTER COLUMN action DROP DEFAULT;

-- Create indexes for EditorActionLog
CREATE INDEX IF NOT EXISTS editor_management_editoractionlog_editor_id_timestamp_idx 
    ON editor_management_editoractionlog(editor_id, timestamp);
CREATE INDEX IF NOT EXISTS editor_management_editoractionlog_action_type_timestamp_idx 
    ON editor_management_editoractionlog(action_type, timestamp);

-- EditorTaskAssignment missing fields
ALTER TABLE editor_management_editortaskassignment
ADD COLUMN IF NOT EXISTS assignment_type VARCHAR(20) DEFAULT 'auto',
ADD COLUMN IF NOT EXISTS assigned_by_id BIGINT REFERENCES users_user(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS review_status VARCHAR(20) DEFAULT 'pending',
ADD COLUMN IF NOT EXISTS started_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS notes TEXT,
ADD COLUMN IF NOT EXISTS editor_rating INTEGER;

-- Create indexes for EditorTaskAssignment
CREATE INDEX IF NOT EXISTS editor_management_editortaskassignment_assigned_editor_id_review_status_idx 
    ON editor_management_editortaskassignment(assigned_editor_id, review_status);
CREATE INDEX IF NOT EXISTS editor_management_editortaskassignment_review_status_assigned_at_idx 
    ON editor_management_editortaskassignment(review_status, assigned_at);
CREATE INDEX IF NOT EXISTS editor_management_editortaskassignment_order_id_idx 
    ON editor_management_editortaskassignment(order_id);

-- EditorNotification missing fields
ALTER TABLE editor_management_editornotification
ADD COLUMN IF NOT EXISTS related_order_id BIGINT REFERENCES orders_order(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS related_task_id BIGINT REFERENCES editor_management_editortaskassignment(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS notification_type VARCHAR(50) DEFAULT 'info';

-- Create index for EditorNotification
CREATE INDEX IF NOT EXISTS editor_management_editornotification_editor_id_is_read_created_at_idx 
    ON editor_management_editornotification(editor_id, is_read, created_at);

