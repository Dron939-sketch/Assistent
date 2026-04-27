-- ============================================
-- 6. Content generations (posts, replies, etc)
-- ============================================
CREATE TABLE content_generations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    type VARCHAR(50) NOT NULL, -- post, reply, marathon_day, story, case
    topic VARCHAR(500),
    
    -- Input
    input_text TEXT,
    input_voice_url TEXT,
    
    -- Output
    output_text TEXT,
    output_metadata JSONB,
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending',
    
    -- Usage
    tokens_used INT,
    cost DECIMAL(10,6),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    published_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_content_generations_user_id ON content_generations(user_id);
CREATE INDEX idx_content_generations_type ON content_generations(type);
CREATE INDEX idx_content_generations_created_at ON content_generations(created_at);

-- ============================================
-- 7. Content calendar (scheduled posts)
-- ============================================
CREATE TABLE content_calendar (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    title VARCHAR(500) NOT NULL,
    content TEXT,
    content_type VARCHAR(50), -- post, story, video, article
    theme VARCHAR(255),
    
    -- Scheduling
    scheduled_for TIMESTAMP WITH TIME ZONE NOT NULL,
    published_at TIMESTAMP WITH TIME ZONE,
    
    -- Status
    status VARCHAR(50) DEFAULT 'scheduled', -- scheduled, published, failed, cancelled
    
    -- VK
    vk_post_id VARCHAR(100),
    vk_post_url TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_content_calendar_user_id ON content_calendar(user_id);
CREATE INDEX idx_content_calendar_scheduled_for ON content_calendar(scheduled_for);
CREATE INDEX idx_content_calendar_status ON content_calendar(status);
