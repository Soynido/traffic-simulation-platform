# Design System: Traffic Simulation Platform

## Overview
Modern, analytics-focused dashboard inspired by Google Analytics 4, Supabase Dashboard, and Datadog. Clean, minimal interface optimized for real-time monitoring and campaign management.

## Design Principles

### 1. **Clarity First**
- Information hierarchy prioritizes critical metrics
- Clean spacing and typography for easy scanning
- Minimal cognitive load for monitoring workflows

### 2. **Real-time Focused** 
- Live updates without page refresh
- Immediate visual feedback for state changes
- Performance-optimized for continuous monitoring

### 3. **Data-Driven**
- Charts and visualizations as primary communication
- Tabular data for detailed inspection
- Progressive disclosure of complexity

## Color Palette

### Core Colors
```css
/* Primary States */
--success: #22C55E;      /* Green - completed, healthy */
--running: #3B82F6;      /* Blue - active, in-progress */
--warning: #F59E0B;      /* Orange - attention needed */
--error: #EF4444;        /* Red - failed, critical */
--pending: #6B7280;      /* Gray - queued, waiting */

/* Data Distinction */
--simulated: #2563EB;    /* Blue - simulated traffic */
--human: #7C3AED;        /* Purple - human baseline */

/* Theme: Light */
--bg-primary: #F9FAFB;   /* Main background */
--bg-secondary: #FFFFFF; /* Card backgrounds */
--text-primary: #111827; /* Main text */
--text-secondary: #6B7280; /* Secondary text */
--border: #E5E7EB;       /* Borders, dividers */

/* Theme: Dark */
--bg-primary-dark: #111827; /* Main background */
--bg-secondary-dark: #1F2937; /* Card backgrounds */
--text-primary-dark: #F9FAFB; /* Main text */
--text-secondary-dark: #9CA3AF; /* Secondary text */
--border-dark: #374151;   /* Borders, dividers */
```

### Status Badge Colors
```css
.status-running { @apply bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200; }
.status-pending { @apply bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200; }
.status-failed { @apply bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200; }
.status-completed { @apply bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200; }
```

## Typography

### Font Stack
```css
/* Primary: System fonts for performance */
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;

/* Monospace: For logs, metrics, IDs */  
font-family: 'SF Mono', 'Monaco', 'Cascadia Code', monospace;
```

### Typography Scale
```css
/* Headers */
.text-4xl { font-size: 2.25rem; line-height: 2.5rem; } /* Page titles */
.text-2xl { font-size: 1.5rem; line-height: 2rem; }   /* Section titles */
.text-lg { font-size: 1.125rem; line-height: 1.75rem; } /* Card titles */

/* Body */
.text-base { font-size: 1rem; line-height: 1.5rem; }   /* Default body */
.text-sm { font-size: 0.875rem; line-height: 1.25rem; } /* Secondary text */
.text-xs { font-size: 0.75rem; line-height: 1rem; }    /* Labels, captions */
```

## Component Library

### 1. KPI Cards (inspired by GA4)
```tsx
interface KPICardProps {
  title: string;
  value: string | number;
  change?: { value: number; period: string };
  status: 'success' | 'warning' | 'error' | 'neutral';
  icon?: React.ReactNode;
}

// Visual: Large number, small change indicator, colored left border
```

### 2. Status Badges (inspired by Airflow)
```tsx
interface StatusBadgeProps {
  status: 'running' | 'pending' | 'completed' | 'failed' | 'paused';
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
}

// Visual: Colored background, white text, rounded, optional icon
```

### 3. Data Tables (inspired by Supabase)
```tsx
interface DataTableProps {
  columns: Column[];
  data: any[];
  pagination?: boolean;
  sorting?: boolean;
  filtering?: boolean;
  realtime?: boolean;
}

// Visual: Clean rows, hover states, inline actions
```

### 4. Charts (Recharts integration)
```tsx
// Line Chart - Sessions over time
<ResponsiveContainer width="100%" height={300}>
  <LineChart data={sessionData}>
    <XAxis dataKey="timestamp" />
    <YAxis />
    <CartesianGrid strokeDasharray="3 3" />
    <Line type="monotone" dataKey="simulated" stroke="var(--simulated)" strokeWidth={2} />
    <Line type="monotone" dataKey="human" stroke="var(--human)" strokeWidth={2} />
    <Tooltip />
    <Legend />
  </LineChart>
</ResponsiveContainer>

// Donut Chart - Campaign distribution
<ResponsiveContainer width="100%" height={250}>
  <PieChart>
    <Pie data={campaignData} dataKey="sessions" nameKey="name" outerRadius={80} innerRadius={40}>
      {campaignData.map((entry, index) => (
        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
      ))}
    </Pie>
    <Tooltip />
  </PieChart>
</ResponsiveContainer>
```

### 5. Real-time Indicators
```tsx
interface LiveIndicatorProps {
  isLive: boolean;
  count?: number;
  label: string;
}

// Visual: Pulsing dot, live count, "Live" badge
```

### 6. Progress Components
```tsx
interface ProgressBarProps {
  current: number;
  total: number;
  status: 'running' | 'completed' | 'failed';
  showPercentage?: boolean;
}

// Visual: Colored fill bar, percentage text, status coloring
```

## Layout System

### Grid Structure (inspired by Datadog)
```tsx
// Main Dashboard Layout
<div className="grid grid-cols-12 gap-6 p-6">
  {/* KPI Cards Row */}
  <div className="col-span-12 grid grid-cols-1 md:grid-cols-4 gap-4">
    <KPICard title="Active Sessions" value={245} status="success" />
    <KPICard title="Success Rate" value="94.2%" status="success" />
    <KPICard title="Avg Duration" value="2m 34s" status="neutral" />
    <KPICard title="Errors" value={12} status="warning" />
  </div>
  
  {/* Charts Row */}
  <div className="col-span-12 lg:col-span-8">
    <SessionChart />
  </div>
  <div className="col-span-12 lg:col-span-4">
    <PersonaDistribution />
  </div>
  
  {/* Data Table */}
  <div className="col-span-12">
    <CampaignTable />
  </div>
</div>
```

### Card Container Pattern
```tsx
// Standard card wrapper for all components
<div className="bg-white dark:bg-gray-900 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
  <div className="flex items-center justify-between mb-4">
    <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
      {title}
    </h3>
    <div className="flex items-center space-x-2">
      {actions}
    </div>
  </div>
  {children}
</div>
```

## Specific Dashboard Sections

### 1. Campaign Management (inspired by Supabase Studio)
```tsx
// Campaign Creation Form
<form className="space-y-6 bg-white dark:bg-gray-900 rounded-lg p-6">
  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
    <Input label="Campaign Name" placeholder="My Test Campaign" />
    <Input label="Target URL" placeholder="https://example.com" />
    <Select label="Persona" options={personas} />
    <Input label="Total Sessions" type="number" />
  </div>
  
  <div className="flex justify-end space-x-3">
    <Button variant="outline">Cancel</Button>
    <Button variant="primary">Create Campaign</Button>
  </div>
</form>

// Campaign Status Overview
<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
  {campaigns.map(campaign => (
    <div key={campaign.id} className="card">
      <div className="flex justify-between items-start mb-3">
        <h4 className="font-medium">{campaign.name}</h4>
        <StatusBadge status={campaign.status} />
      </div>
      <div className="space-y-2 text-sm text-gray-600">
        <div>Target: {campaign.targetUrl}</div>
        <div>Progress: {campaign.completed}/{campaign.total} sessions</div>
        <ProgressBar current={campaign.completed} total={campaign.total} />
      </div>
      <div className="flex justify-end mt-4 space-x-2">
        {campaign.status === 'running' && (
          <Button size="sm" variant="outline">Pause</Button>
        )}
        {campaign.status === 'paused' && (
          <Button size="sm" variant="primary">Resume</Button>
        )}
      </div>
    </div>
  ))}
</div>
```

### 2. Real-time Monitoring (inspired by Datadog Live View)
```tsx
// Live Session Feed
<div className="bg-white dark:bg-gray-900 rounded-lg">
  <div className="flex items-center justify-between p-4 border-b">
    <div className="flex items-center space-x-3">
      <LiveIndicator isLive={true} count={activeCount} label="Active Sessions" />
      <h3 className="font-semibold">Live Activity</h3>
    </div>
    <div className="flex items-center space-x-2">
      <Button size="sm" variant="outline">Filters</Button>
      <Button size="sm" variant="outline">Export</Button>
    </div>
  </div>
  
  <div className="max-h-96 overflow-y-auto">
    {sessions.map(session => (
      <div key={session.id} className="flex items-center justify-between p-4 border-b hover:bg-gray-50">
        <div className="flex items-center space-x-4">
          <StatusBadge status={session.status} size="sm" />
          <div>
            <div className="font-medium text-sm">{session.campaignName}</div>
            <div className="text-xs text-gray-500">{session.targetUrl}</div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-sm font-medium">{session.duration}</div>
          <div className="text-xs text-gray-500">{session.pagesVisited} pages</div>
        </div>
      </div>
    ))}
  </div>
</div>
```

### 3. Analytics Comparison (inspired by Hotjar + Metabase)
```tsx
// Human vs Simulated Traffic Comparison
<div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
  {/* Side-by-side metrics */}
  <div className="card">
    <h3 className="text-lg font-semibold mb-4">Simulated Traffic</h3>
    <div className="space-y-3">
      <MetricRow label="Avg Session Duration" value="2m 45s" color="simulated" />
      <MetricRow label="Pages per Session" value="4.2" color="simulated" />
      <MetricRow label="Bounce Rate" value="23%" color="simulated" />
      <MetricRow label="Action Variance" value="0.34" color="simulated" />
    </div>
  </div>
  
  <div className="card">
    <h3 className="text-lg font-semibold mb-4">Human Baseline</h3>
    <div className="space-y-3">
      <MetricRow label="Avg Session Duration" value="3m 12s" color="human" />
      <MetricRow label="Pages per Session" value="3.8" color="human" />
      <MetricRow label="Bounce Rate" value="31%" color="human" />
      <MetricRow label="Action Variance" value="0.67" color="human" />
    </div>
  </div>
  
  {/* Comparison Chart */}
  <div className="col-span-2 card">
    <h3 className="text-lg font-semibold mb-4">Behavioral Comparison</h3>
    <ComparisonChart simulatedData={simulated} humanData={human} />
  </div>
</div>
```

## Tech Stack Integration

### Dependencies (package.json)
```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "typescript": "^5.0.0",
    "tailwindcss": "^3.3.0",
    "@tailwindui/react": "^0.1.1",
    "recharts": "^2.8.0",
    "@radix-ui/react-avatar": "^1.0.4",
    "@radix-ui/react-badge": "^1.0.0",
    "@radix-ui/react-button": "^1.0.0",
    "@radix-ui/react-card": "^1.0.0",
    "lucide-react": "^0.294.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0"
  }
}
```

### TailwindCSS Configuration
```js
// tailwind.config.js
module.exports = {
  darkMode: ['class'],
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        success: '#22C55E',
        running: '#3B82F6', 
        warning: '#F59E0B',
        error: '#EF4444',
        pending: '#6B7280',
        simulated: '#2563EB',
        human: '#7C3AED',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    }
  },
  plugins: [require('@tailwindcss/forms')]
}
```

## Performance Considerations

### 1. **Real-time Updates**
- WebSocket connection for live data
- Debounced updates to prevent UI thrashing
- Virtual scrolling for large datasets

### 2. **Chart Optimization**
- Data sampling for large time series
- Canvas rendering for high-frequency updates
- Lazy loading for dashboard sections

### 3. **Responsive Design**
- Mobile-first approach
- Collapsible sidebar navigation
- Responsive grid system for all breakpoints

Cette spécification design suit exactement tes inspirations tout en restant techniquement réalisable avec le stack gratuit (React + TailwindCSS + shadcn/ui + Recharts). Le tout s'intègre parfaitement avec notre architecture technique existante.