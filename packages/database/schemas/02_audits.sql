-- ============================================
-- 4. VK Audits (module 1.1)
-- ============================================
CREATE TABLE vk_audits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Input
    vk_page_url VARCHAR(500) NOT NULL,
    vk_group_id VARCHAR(100) NOT NULL,
    
    -- Results (JSON)
    result JSONB NOT NULL,
    score INT, -- 0-100
    recommendations JSONB,
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending', -- pending, processing, completed, failed
    error_message TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_vk_audits_user_id ON vk_audits(user_id);
CREATE INDEX idx_vk_audits_status ON vk_audits(status);
CREATE INDEX idx_vk_audits_created_at ON vk_audits(created_at);

-- ============================================
-- 5. VK Audit details (scores per category)
-- ============================================
CREATE TABLE vk_audit_details (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audit_id UUID NOT NULL REFERENCES vk_audits(id) ON DELETE CASCADE,
    
    category VARCHAR(100) NOT NULL, -- cover, avatar, pinned, content, comments, etc
    score INT,
    max_score INT,
    issues JSONB,
    recommendations JSONB,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_vk_audit_details_audit_id ON vk_audit_details(audit_id);
