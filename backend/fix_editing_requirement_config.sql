-- Quick fix to create EditingRequirementConfig table
-- Run with: docker-compose exec db psql -U postgres -d writingsondo -f fix_editing_requirement_config.sql

CREATE TABLE IF NOT EXISTS order_configs_editingrequirementconfig (
    id BIGSERIAL PRIMARY KEY,
    website_id BIGINT NOT NULL REFERENCES websites_website(id) ON DELETE CASCADE,
    enable_editing_by_default BOOLEAN DEFAULT TRUE,
    skip_editing_for_urgent BOOLEAN DEFAULT TRUE,
    allow_editing_for_early_submissions BOOLEAN DEFAULT TRUE,
    early_submission_hours_threshold INTEGER DEFAULT 24,
    editing_required_for_first_orders BOOLEAN DEFAULT TRUE,
    editing_required_for_high_value BOOLEAN DEFAULT TRUE,
    high_value_threshold NUMERIC(10, 2) DEFAULT 300.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by_id BIGINT REFERENCES users_user(id) ON DELETE SET NULL,
    CONSTRAINT unique_website UNIQUE (website_id)
);

CREATE INDEX IF NOT EXISTS order_configs_editingrequirementconfig_website_id_idx 
    ON order_configs_editingrequirementconfig(website_id);

CREATE INDEX IF NOT EXISTS order_configs_editingrequirementconfig_created_by_id_idx 
    ON order_configs_editingrequirementconfig(created_by_id);

