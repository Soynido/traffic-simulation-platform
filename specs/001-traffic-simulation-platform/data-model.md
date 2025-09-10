# Data Model: Traffic Simulation Platform

## Core Entities

### Persona
Represents user behavior profiles for simulation
```sql
CREATE TABLE personas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    session_duration_min INTEGER NOT NULL CHECK (session_duration_min > 0),
    session_duration_max INTEGER NOT NULL CHECK (session_duration_max >= session_duration_min),
    pages_min INTEGER NOT NULL CHECK (pages_min > 0),
    pages_max INTEGER NOT NULL CHECK (pages_max >= pages_min),
    actions_per_page_min INTEGER NOT NULL DEFAULT 1,
    actions_per_page_max INTEGER NOT NULL DEFAULT 10,
    scroll_probability DECIMAL(3,2) NOT NULL DEFAULT 0.8 CHECK (scroll_probability BETWEEN 0 AND 1),
    click_probability DECIMAL(3,2) NOT NULL DEFAULT 0.6 CHECK (click_probability BETWEEN 0 AND 1),
    typing_probability DECIMAL(3,2) NOT NULL DEFAULT 0.1 CHECK (typing_probability BETWEEN 0 AND 1),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

**Validation Rules**:
- Name must be unique
- Duration and page ranges must be logical (min <= max)
- Probabilities must be between 0 and 1

**State Transitions**: Static configuration entity (no state changes)

### Campaign
Represents simulation campaign configuration
```sql
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    target_url VARCHAR(500) NOT NULL,
    total_sessions INTEGER NOT NULL CHECK (total_sessions > 0),
    concurrent_sessions INTEGER NOT NULL DEFAULT 10 CHECK (concurrent_sessions > 0),
    status campaign_status NOT NULL DEFAULT 'pending',
    persona_id UUID NOT NULL REFERENCES personas(id),
    rate_limit_delay_ms INTEGER NOT NULL DEFAULT 1000 CHECK (rate_limit_delay_ms >= 100),
    user_agent_rotation BOOLEAN NOT NULL DEFAULT true,
    respect_robots_txt BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT valid_session_count CHECK (concurrent_sessions <= total_sessions)
);

CREATE TYPE campaign_status AS ENUM ('pending', 'running', 'paused', 'completed', 'failed');
```

**State Transitions**:
- pending → running (campaign started)
- running → paused (manual pause)
- running → completed (all sessions finished)
- running → failed (critical error)
- paused → running (resume)

### Session
Represents individual simulation sessions
```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    persona_id UUID NOT NULL REFERENCES personas(id),
    status session_status NOT NULL DEFAULT 'pending',
    start_url VARCHAR(500) NOT NULL,
    user_agent TEXT NOT NULL,
    viewport_width INTEGER NOT NULL DEFAULT 1920,
    viewport_height INTEGER NOT NULL DEFAULT 1080,
    session_duration_ms INTEGER,
    pages_visited INTEGER DEFAULT 0,
    total_actions INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    INDEX idx_sessions_campaign_status (campaign_id, status),
    INDEX idx_sessions_created_at (created_at)
);

CREATE TYPE session_status AS ENUM ('pending', 'running', 'completed', 'failed', 'timeout');
```

**State Transitions**:
- pending → running (session started)
- running → completed (successful completion)
- running → failed (error occurred)
- running → timeout (exceeded max duration)

### PageVisit
Represents individual page visits within sessions
```sql
CREATE TABLE page_visits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    url VARCHAR(500) NOT NULL,
    title TEXT,
    visit_order INTEGER NOT NULL CHECK (visit_order > 0),
    arrived_at TIMESTAMP WITH TIME ZONE NOT NULL,
    left_at TIMESTAMP WITH TIME ZONE,
    dwell_time_ms INTEGER GENERATED ALWAYS AS (
        EXTRACT(EPOCH FROM (left_at - arrived_at)) * 1000
    ) STORED,
    actions_count INTEGER DEFAULT 0,
    scroll_depth_percent INTEGER DEFAULT 0 CHECK (scroll_depth_percent BETWEEN 0 AND 100),
    
    INDEX idx_page_visits_session (session_id, visit_order),
    INDEX idx_page_visits_url (url),
    UNIQUE(session_id, visit_order)
);
```

### Action
Represents user actions within page visits
```sql
CREATE TABLE actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    page_visit_id UUID NOT NULL REFERENCES page_visits(id) ON DELETE CASCADE,
    action_type action_type NOT NULL,
    element_selector TEXT,
    element_text TEXT,
    coordinates_x INTEGER,
    coordinates_y INTEGER,
    input_value TEXT,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    action_order INTEGER NOT NULL CHECK (action_order > 0),
    duration_ms INTEGER DEFAULT 0,
    
    INDEX idx_actions_page_visit (page_visit_id, action_order),
    INDEX idx_actions_type_timestamp (action_type, timestamp),
    UNIQUE(page_visit_id, action_order)
);

CREATE TYPE action_type AS ENUM (
    'click', 'double_click', 'right_click',
    'scroll', 'scroll_to_element',
    'type', 'clear', 'select',
    'hover', 'drag_and_drop',
    'key_press', 'page_load', 'page_unload'
);
```

## Analytics Entities

### SessionAnalytics
Aggregated session metrics for faster reporting
```sql
CREATE TABLE session_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE UNIQUE,
    campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    persona_id UUID NOT NULL REFERENCES personas(id),
    
    -- Timing metrics
    total_duration_ms INTEGER NOT NULL,
    avg_page_dwell_time_ms DECIMAL(10,2),
    median_page_dwell_time_ms INTEGER,
    
    -- Navigation metrics
    pages_visited INTEGER NOT NULL,
    navigation_depth INTEGER NOT NULL,
    bounce_rate DECIMAL(3,2), -- 0 if more than 1 page, 1 if only 1 page
    
    -- Interaction metrics
    total_actions INTEGER NOT NULL,
    actions_per_page DECIMAL(4,2),
    click_through_rate DECIMAL(3,2),
    scroll_engagement DECIMAL(3,2), -- average scroll depth
    
    -- Behavioral patterns
    action_variance DECIMAL(6,3), -- variance in action timing
    rhythm_score DECIMAL(3,2), -- regularity of actions (0=robotic, 1=human-like)
    pause_distribution JSONB, -- distribution of pauses between actions
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    
    INDEX idx_session_analytics_campaign (campaign_id),
    INDEX idx_session_analytics_persona (persona_id),
    INDEX idx_session_analytics_created_at (created_at)
);
```

### CampaignAnalytics
Campaign-level aggregated metrics
```sql
CREATE TABLE campaign_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE UNIQUE,
    
    -- Completion metrics
    total_sessions INTEGER NOT NULL,
    completed_sessions INTEGER NOT NULL,
    failed_sessions INTEGER NOT NULL,
    success_rate DECIMAL(3,2) NOT NULL,
    
    -- Performance metrics
    avg_session_duration_ms DECIMAL(12,2),
    avg_pages_per_session DECIMAL(4,2),
    avg_actions_per_session DECIMAL(6,2),
    
    -- Quality metrics
    avg_rhythm_score DECIMAL(3,2),
    behavioral_variance DECIMAL(6,3),
    detection_risk_score DECIMAL(3,2), -- 0=undetectable, 1=obvious bot
    
    -- Resource usage
    total_runtime_ms BIGINT,
    avg_cpu_usage DECIMAL(3,2),
    peak_memory_mb INTEGER,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

## Relationships

### Entity Relationship Summary
- **Campaign** 1:N **Session** (one campaign runs many sessions)
- **Persona** 1:N **Session** (one persona used by many sessions)
- **Persona** 1:N **Campaign** (one persona can be used by multiple campaigns)
- **Session** 1:N **PageVisit** (one session visits many pages)
- **PageVisit** 1:N **Action** (one page visit has many actions)
- **Session** 1:1 **SessionAnalytics** (one analytics record per session)
- **Campaign** 1:1 **CampaignAnalytics** (one analytics record per campaign)

## Indexes and Performance

### Query Optimization Indexes
```sql
-- Campaign monitoring queries
CREATE INDEX idx_campaigns_status_created ON campaigns(status, created_at DESC);

-- Session progress tracking
CREATE INDEX idx_sessions_campaign_status_time ON sessions(campaign_id, status, created_at);

-- Real-time analytics
CREATE INDEX idx_page_visits_session_time ON page_visits(session_id, arrived_at);
CREATE INDEX idx_actions_timestamp ON actions(timestamp) WHERE timestamp > now() - interval '1 hour';

-- Analytics queries
CREATE INDEX idx_session_analytics_metrics ON session_analytics(campaign_id, total_duration_ms, pages_visited);
CREATE INDEX idx_campaign_analytics_updated ON campaign_analytics(updated_at DESC);
```

### Partitioning Strategy
```sql
-- Partition page_visits by date for time-series performance
ALTER TABLE page_visits PARTITION BY RANGE (arrived_at);

-- Partition actions by timestamp for better insert performance
ALTER TABLE actions PARTITION BY RANGE (timestamp);
```

## Data Validation Rules

### Business Rules Enforcement
1. **Session Consistency**: session.pages_visited must equal count of page_visits
2. **Action Ordering**: action.action_order must be sequential within page_visit
3. **Timing Consistency**: page_visit.left_at must be >= arrived_at
4. **Campaign Limits**: concurrent_sessions <= total_sessions
5. **Persona Ranges**: All min/max values must be logically consistent

### Database Constraints
- Foreign key constraints ensure referential integrity
- Check constraints validate data ranges
- Unique constraints prevent duplicate entries
- NOT NULL constraints ensure required data

## Data Lifecycle

### Data Retention
- **Active Sessions**: Keep indefinitely for ongoing campaigns
- **Completed Sessions**: Keep detailed data for 90 days, analytics forever
- **Failed Sessions**: Keep for 30 days for debugging
- **Analytics**: Keep aggregated data indefinitely

### Archival Strategy
- Move detailed session data to cold storage after 90 days
- Maintain analytics tables for historical reporting
- Automated cleanup of expired session details