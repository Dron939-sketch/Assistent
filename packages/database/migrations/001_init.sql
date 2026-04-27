-- ============================================
-- MIGRATION: 001_init
-- Creates all tables in correct order and seeds
-- baseline tenants. Admin users are created via
-- the application bootstrap, never hardcoded here.
-- ============================================

\i packages/database/schemas/01_tenants.sql
\i packages/database/schemas/02_audits.sql
\i packages/database/schemas/03_content.sql
\i packages/database/schemas/04_marathons.sql
\i packages/database/schemas/05_funnel.sql
\i packages/database/schemas/06_analytics.sql

-- ============================================
-- Row Level Security (RLS) for multi-tenancy
-- Apply tenant_isolation policy on every tenant-scoped table.
-- ============================================

DO $$
DECLARE
    t TEXT;
    tables TEXT[] := ARRAY[
        'users', 'subscriptions',
        'vk_audits', 'vk_audit_details',
        'content_generations', 'content_calendar',
        'marathons', 'marathon_participants',
        'auto_funnels', 'leads',
        'daily_analytics', 'leverage_points'
    ];
BEGIN
    FOREACH t IN ARRAY tables LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', t);
        EXECUTE format(
            'DROP POLICY IF EXISTS tenant_isolation ON %I', t
        );
        EXECUTE format(
            'CREATE POLICY tenant_isolation ON %I '
            'USING (tenant_id = (SELECT id FROM tenants '
            'WHERE tenant_id = current_setting(''app.current_tenant'', TRUE)::VARCHAR))',
            t
        );
    END LOOP;
END $$;

ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_self ON tenants;
CREATE POLICY tenant_self ON tenants
    USING (tenant_id = current_setting('app.current_tenant', TRUE)::VARCHAR);

-- ============================================
-- Seed data (default tenants only)
-- ============================================

INSERT INTO tenants (tenant_id, name, specialization, config, branding, ai_config, status)
VALUES
    ('nutrition', 'NutroPult', 'nutrition',
     '{"tier_features": {"start": ["auto_funnel"], "pro": ["audit_vk", "post_generator"], "expert": ["marathon_builder"]}}'::jsonb,
     '{"primary_color": "#2E7D32"}'::jsonb,
     '{"model": "gpt-4-turbo-preview"}'::jsonb,
     'active'),

    ('psychology', 'PsyFlow', 'psychology',
     '{"tier_features": {"start": ["auto_funnel"], "pro": ["audit_vk", "post_generator"], "expert": ["marathon_builder"]}}'::jsonb,
     '{"primary_color": "#4A90E2"}'::jsonb,
     '{"model": "gpt-4-turbo-preview"}'::jsonb,
     'active'),

    ('tarot', 'TarologBot', 'tarot',
     '{"tier_features": {"start": ["auto_funnel"], "pro": ["audit_vk", "post_generator"], "expert": ["marathon_builder"]}}'::jsonb,
     '{"primary_color": "#9C27B0"}'::jsonb,
     '{"model": "gpt-4-turbo-preview"}'::jsonb,
     'active')
ON CONFLICT (tenant_id) DO NOTHING;
