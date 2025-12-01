-- Quick fix to add missing EditorProfile fields
-- Run with: docker-compose exec -T db psql -U postgres -d writingsondo < fix_editor_profile_fields.sql

ALTER TABLE editor_management_editorprofile
ADD COLUMN IF NOT EXISTS can_self_assign BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS max_concurrent_tasks INTEGER DEFAULT 5;

