-- ============================================
-- MIGRATION: 001_init
-- Creates all tables in correct order
-- ============================================

-- Run in order:
\i packages/database/schemas/01_tenants.sql
\i packages/database/schemas/02_audits.sql
\i packages/database/schemas/03_content.sql
\i packages/database/schemas/04_marathons.sql
\i packages/database/schemas/05_funnel.sql
\i packages/database/schemas/06_analytics.sql

-- ============================================
-- Row Level Security (RLS) for multi-tenancy
-- ============================================

-- Enable RLS on all tables
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE vk_audits ENABLE ROW LEVEL SECURITY;
ALTER TABLE vk_audit_details ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_generations ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_calendar ENABLE ROW LEVEL SECURITY;
ALTER TABLE marathons ENABLE ROW LEVEL SECURITY;
ALTER TABLE marathon_participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE auto_funnels ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE leverage_points ENABLE ROW LEVEL SECURITY;

-- Policies: users can only see their own tenant's data
CREATE POLICY tenant_isolation ON users
    USING (tenant_id = (SELECT id FROM tenants WHERE tenant_id = current_setting('app.current_tenant', TRUE)::VARCHAR));

-- ... similar policies for other tables (simplified for now)

-- ============================================
-- Seed data (default tenants)
-- ============================================

INSERT INTO tenants (tenant_id, name, specialization, config, branding, ai_config, status)
VALUES 
    ('nutrition', 'NutroPult', 'nutrition', 
     '{"tier_features": {"start": ["auto_funnel"], "pro": ["audit_vk", "post_generator"], "expert": ["marathon_builder"]}}'::jsonb,
     '{"primary_color": "#2E7D32"}'::jsonb,
     '{"model": "gpt-4"}'::jsonb,
     'active'),
    
    ('psychology', 'PsyFlow', 'psychology',
     '{"tier_features": {"start": ["auto_funnel"], "pro": ["audit_vk", "post_generator"], "expert": ["marathon_builder"]}}'::jsonb,
     '{"primary_color": "#4A90E2"}'::jsonb,
     '{"model": "gpt-4"}'::jsonb,
     'active'),
    
    ('tarot', 'TarologBot', 'tarot',
     '{"tier_features": {"start": ["auto_funnel"], "pro": ["audit_vk", "post_generator"], "expert": ["marathon_builder"]}}'::jsonb,
     '{"primary_color": "#9C27B0"}'::jsonb,
     '{"model": "gpt-4"}'::jsonb,
     'active');

-- Create default admin user (password: admin123)
INSERT INTO users (tenant_id, email, password_hash, full_name, current_tier)
SELECT id, 'admin@fishflow.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtY1YZZKxQqHG', 'Admin', 'expert'
FROM tenants WHERE tenant_id = 'nutrition';
