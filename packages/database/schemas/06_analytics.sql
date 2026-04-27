-- ============================================
-- 12. Daily analytics (aggregated)
-- ============================================
CREATE TABLE daily_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    day DATE NOT NULL,
    
    -- Growth metrics
    new_subscribers INT DEFAULT 0,
    total_subscribers INT DEFAULT 0,
    lost_subscribers INT DEFAULT 0,
    
    -- Engagement metrics
    posts_count INT DEFAULT 0,
    posts_reach INT DEFAULT 0,
    posts_likes INT DEFAULT 0,
    posts_comments INT DEFAULT 0,
    posts_shares INT DEFAULT 0,
    er DECIMAL(5,2), -- engagement rate
    
    -- Leads metrics
    new_leads INT DEFAULT 0,
    leads_consultation INT DEFAULT 0, -- booked consultation
    leads_client INT DEFAULT 0, -- became client
    leads_lost INT DEFAULT 0,
    
    -- Revenue
    revenue DECIMAL(10,2) DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id, day)
);

CREATE INDEX idx_daily_analytics_user_id ON daily_analytics(user_id);
CREATE INDEX idx_daily_analytics_day ON daily_analytics(day);

-- ============================================
-- 13. Leverage points (рычаги) history
-- ============================================
CREATE TABLE leverage_points (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    date DATE NOT NULL,
    
    -- Suggestion
    action VARCHAR(500) NOT NULL,
    effort_hours DECIMAL(5,2),
    expected_impact VARCHAR(255),
    
    -- Whether user completed
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Actual result
    actual_impact TEXT,
    actual_leads_increase INT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_leverage_points_user_id ON leverage_points(user_id);
CREATE INDEX idx_leverage_points_date ON leverage_points(date);
