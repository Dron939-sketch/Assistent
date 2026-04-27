-- ============================================
-- FISHFLOW DATABASE SCHEMA
-- Tenant management
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 1. Tenants table (multi-tenant core)
-- ============================================
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    domain VARCHAR(255),
    
    -- Configuration
    config JSONB NOT NULL DEFAULT '{}',
    branding JSONB NOT NULL DEFAULT '{}',
    ai_config JSONB NOT NULL DEFAULT '{}',
    
    -- Status
    status VARCHAR(50) DEFAULT 'active', -- active, suspended, deleted
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Indexes
CREATE INDEX idx_tenants_tenant_id ON tenants(tenant_id);
CREATE INDEX idx_tenants_domain ON tenants(domain);
CREATE INDEX idx_tenants_status ON tenants(status);

-- ============================================
-- 2. Users table (multi-tenant)
-- ============================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Auth
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    
    -- Profile
    full_name VARCHAR(255),
    avatar_url TEXT,
    phone VARCHAR(50),
    
    -- VK integration
    vk_group_id VARCHAR(100),
    vk_access_token TEXT,
    vk_group_name VARCHAR(255),
    
    -- Telegram integration
    telegram_bot_token TEXT,
    telegram_chat_id VARCHAR(100),
    
    -- Subscription
    current_tier VARCHAR(50) DEFAULT 'start', -- start, pro, expert
    subscription_status VARCHAR(50) DEFAULT 'trial', -- trial, active, expired, cancelled
    subscription_expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Settings
    voice_style TEXT,
    uniqueness TEXT,
    forbidden_topics TEXT[] DEFAULT '{}',
    
    -- Stats
    total_leads INT DEFAULT 0,
    total_clients INT DEFAULT 0,
    total_revenue DECIMAL(10,2) DEFAULT 0,
    
    -- Timestamps
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(tenant_id, email)
);

-- Indexes
CREATE INDEX idx_users_tenant_id ON users(tenant_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_current_tier ON users(current_tier);
CREATE INDEX idx_users_subscription_status ON users(subscription_status);

-- ============================================
-- 3. Subscriptions table (billing history)
-- ============================================
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    tier VARCHAR(50) NOT NULL, -- start, pro, expert
    status VARCHAR(50) NOT NULL, -- active, past_due, cancelled, expired
    
    -- Payment
    provider VARCHAR(50), -- stripe, yookassa
    provider_subscription_id VARCHAR(255),
    provider_customer_id VARCHAR(255),
    
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'RUB',
    
    -- Periods
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
