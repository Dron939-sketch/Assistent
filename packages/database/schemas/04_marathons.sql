-- ============================================
-- 8. Marathons
-- ============================================
CREATE TABLE marathons (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Structure
    duration_days INT NOT NULL,
    goals JSONB,
    
    -- Content
    structure JSONB, -- days, topics, tasks, bonuses
    generated_content JSONB, -- all posts, tasks, emails
    
    -- Settings
    platform VARCHAR(50) DEFAULT 'telegram', -- telegram, vk, whatsapp
    is_free BOOLEAN DEFAULT TRUE,
    price DECIMAL(10,2),
    
    -- Stats
    participants_count INT DEFAULT 0,
    completed_count INT DEFAULT 0,
    conversion_count INT DEFAULT 0, -- converted to paid
    conversion_revenue DECIMAL(10,2) DEFAULT 0,
    
    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, active, completed, archived
    
    -- Scheduling
    starts_at TIMESTAMP WITH TIME ZONE,
    ends_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_marathons_user_id ON marathons(user_id);
CREATE INDEX idx_marathons_status ON marathons(status);
CREATE INDEX idx_marathons_starts_at ON marathons(starts_at);

-- ============================================
-- 9. Marathon participants
-- ============================================
CREATE TABLE marathon_participants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    marathon_id UUID NOT NULL REFERENCES marathons(id) ON DELETE CASCADE,
    
    -- Participant info
    name VARCHAR(255),
    contact VARCHAR(255), -- phone, tg username, email
    source VARCHAR(255), -- how they found
    
    -- Progress
    current_day INT DEFAULT 1,
    completed_days INT[] DEFAULT '{}',
    homework_submissions JSONB,
    homework_scores JSONB,
    
    -- Status
    status VARCHAR(50) DEFAULT 'active', -- active, completed, dropped
    
    -- Conversion
    converted_to_client BOOLEAN DEFAULT FALSE,
    converted_value DECIMAL(10,2),
    converted_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_active_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_marathon_participants_marathon_id ON marathon_participants(marathon_id);
CREATE INDEX idx_marathon_participants_status ON marathon_participants(status);
