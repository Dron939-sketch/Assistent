-- ============================================
-- 10. Auto funnel (автоворонка)
-- ============================================
CREATE TABLE auto_funnels (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    name VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Trigger rules
    trigger_keywords TEXT[],
    trigger_on_contains BOOLEAN DEFAULT TRUE,
    
    -- Response flow
    flow_steps JSONB, -- [{step:1, message:"...", delay_minutes:0, action:"ask_phone"}, ...]
    
    -- Advanced
    custom_prompt TEXT,
    use_ai BOOLEAN DEFAULT TRUE,
    
    -- Stats
    total_triggers INT DEFAULT 0,
    total_converted INT DEFAULT 0, -- leads that went to consultation
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_auto_funnels_user_id ON auto_funnels(user_id);
CREATE INDEX idx_auto_funnels_is_active ON auto_funnels(is_active);

-- ============================================
-- 11. Leads (from auto funnel)
-- ============================================
CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Source
    source VARCHAR(100) NOT NULL, -- vk_direct, vk_comment, telegram, marathon, landing
    funnel_id UUID REFERENCES auto_funnels(id),
    
    -- Contact
    contact VARCHAR(255) NOT NULL, -- phone, tg, email
    name VARCHAR(255),
    vk_user_id VARCHAR(100),
    tg_user_id VARCHAR(100),
    
    -- Conversation history
    conversation JSONB, -- full chat history
    
    -- Status
    status VARCHAR(50) DEFAULT 'new', -- new, contacted, consultation_booked, client, lost
    
    -- Consultation
    booked_at TIMESTAMP WITH TIME ZONE,
    consultation_link TEXT,
    
    -- Value
    estimated_value DECIMAL(10,2),
    actual_value DECIMAL(10,2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_leads_user_id ON leads(user_id);
CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_created_at ON leads(created_at);
CREATE INDEX idx_leads_contact ON leads(contact);
