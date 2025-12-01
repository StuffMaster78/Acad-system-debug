-- Quick fix to add content_type fields to Ticket model
-- Run with: docker-compose exec -T db psql -U postgres -d writingsondo < fix_tickets_content_type.sql

ALTER TABLE tickets_ticket
ADD COLUMN IF NOT EXISTS content_type_id INTEGER REFERENCES django_content_type(id) ON DELETE CASCADE,
ADD COLUMN IF NOT EXISTS object_id INTEGER;

