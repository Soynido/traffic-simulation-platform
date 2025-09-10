// Types partagés entre frontend et backend
// Ces types définissent le contrat de données de l'application

// ===== TYPES DE BASE =====

export interface BaseEntity {
  id: string;
  createdAt: Date;
  updatedAt: Date;
}

// ===== PERSONA TYPES =====

export interface Persona extends BaseEntity {
  name: string;
  description: string;
  behaviorProfile: BehaviorProfile;
  demographics: Demographics;
  technicalProfile: TechnicalProfile;
  isActive: boolean;
}

export interface BehaviorProfile {
  browsingSpeed: 'slow' | 'normal' | 'fast';
  clickPattern: 'random' | 'systematic' | 'hesitant';
  scrollBehavior: 'smooth' | 'jumpy' | 'minimal';
  sessionDuration: {
    min: number; // minutes
    max: number; // minutes
  };
  pageViewsPerSession: {
    min: number;
    max: number;
  };
  timeOnPage: {
    min: number; // seconds
    max: number; // seconds
  };
}

export interface Demographics {
  age: {
    min: number;
    max: number;
  };
  gender: 'male' | 'female' | 'other' | 'prefer_not_to_say';
  location: {
    country: string;
    region?: string;
    city?: string;
  };
  interests: string[];
  occupation?: string;
}

export interface TechnicalProfile {
  deviceTypes: DeviceType[];
  browsers: BrowserInfo[];
  operatingSystems: OSInfo[];
  screenResolutions: ScreenResolution[];
  connectionTypes: ConnectionType[];
  timezone: string;
}

export interface DeviceType {
  type: 'desktop' | 'mobile' | 'tablet';
  probability: number; // 0-1
}

export interface BrowserInfo {
  name: string;
  version: string;
  userAgent: string;
  probability: number; // 0-1
}

export interface OSInfo {
  name: string;
  version: string;
  probability: number; // 0-1
}

export interface ScreenResolution {
  width: number;
  height: number;
  probability: number; // 0-1
}

export interface ConnectionType {
  type: 'wifi' | '4g' | '5g' | 'ethernet' | '3g';
  speed: 'slow' | 'medium' | 'fast';
  probability: number; // 0-1
}

// ===== CAMPAIGN TYPES =====

export interface Campaign extends BaseEntity {
  name: string;
  description: string;
  targetUrl: string;
  personaIds: string[];
  simulationConfig: SimulationConfig;
  status: CampaignStatus;
  scheduledStart?: Date;
  scheduledEnd?: Date;
  actualStart?: Date;
  actualEnd?: Date;
  metrics: CampaignMetrics;
}

export interface SimulationConfig {
  concurrentSessions: number;
  sessionInterval: number; // seconds between session starts
  duration: number; // total duration in minutes
  randomization: RandomizationConfig;
  behaviorVariation: number; // 0-1, how much to vary from persona behavior
}

export interface RandomizationConfig {
  enabled: boolean;
  timeVariation: number; // 0-1, variation in timing
  actionVariation: number; // 0-1, variation in actions
  pathVariation: number; // 0-1, variation in navigation paths
}

export type CampaignStatus = 
  | 'draft'
  | 'scheduled'
  | 'running'
  | 'paused'
  | 'completed'
  | 'cancelled'
  | 'error';

export interface CampaignMetrics {
  totalSessions: number;
  completedSessions: number;
  failedSessions: number;
  averageSessionDuration: number;
  totalPageViews: number;
  uniquePageViews: number;
  bounceRate: number;
  conversionRate: number;
}

// ===== SESSION TYPES =====

export interface Session extends BaseEntity {
  campaignId: string;
  personaId: string;
  sessionId: string; // unique session identifier
  status: SessionStatus;
  startTime: Date;
  endTime?: Date;
  duration?: number; // seconds
  userAgent: string;
  ipAddress: string;
  referrer?: string;
  pageVisits: PageVisit[];
  actions: Action[];
  metrics: SessionMetrics;
}

export type SessionStatus = 
  | 'pending'
  | 'running'
  | 'completed'
  | 'failed'
  | 'cancelled';

export interface PageVisit extends BaseEntity {
  sessionId: string;
  url: string;
  title: string;
  timestamp: Date;
  duration: number; // seconds spent on page
  scrollDepth: number; // 0-1, how far user scrolled
  viewportSize: ViewportSize;
  referrer?: string;
  actions: Action[];
}

export interface ViewportSize {
  width: number;
  height: number;
}

export interface Action extends BaseEntity {
  sessionId: string;
  pageVisitId?: string;
  type: ActionType;
  timestamp: Date;
  coordinates?: Coordinates;
  element?: ElementInfo;
  data?: Record<string, any>;
  duration?: number; // milliseconds
}

export type ActionType = 
  | 'click'
  | 'scroll'
  | 'hover'
  | 'focus'
  | 'blur'
  | 'input'
  | 'submit'
  | 'navigate'
  | 'resize'
  | 'keypress'
  | 'mousemove'
  | 'mousedown'
  | 'mouseup';

export interface Coordinates {
  x: number;
  y: number;
}

export interface ElementInfo {
  tagName: string;
  id?: string;
  className?: string;
  text?: string;
  attributes?: Record<string, string>;
}

export interface SessionMetrics {
  totalPageViews: number;
  totalActions: number;
  averageTimeOnPage: number;
  bounceRate: number;
  scrollDepth: number;
  clickThroughRate: number;
  formInteractions: number;
  errorCount: number;
}

// ===== ANALYTICS TYPES =====

export interface Analytics extends BaseEntity {
  campaignId: string;
  sessionId?: string;
  type: AnalyticsType;
  timestamp: Date;
  data: AnalyticsData;
  metadata?: Record<string, any>;
}

export type AnalyticsType = 
  | 'session_start'
  | 'session_end'
  | 'page_view'
  | 'action'
  | 'error'
  | 'performance'
  | 'conversion';

export interface AnalyticsData {
  [key: string]: any;
}

export interface CampaignAnalytics {
  campaignId: string;
  period: TimePeriod;
  metrics: CampaignMetrics;
  trends: TrendData[];
  comparisons: ComparisonData[];
  insights: Insight[];
}

export interface TimePeriod {
  start: Date;
  end: Date;
  granularity: 'minute' | 'hour' | 'day' | 'week' | 'month';
}

export interface TrendData {
  timestamp: Date;
  value: number;
  metric: string;
}

export interface ComparisonData {
  metric: string;
  current: number;
  previous: number;
  change: number; // percentage change
  trend: 'up' | 'down' | 'stable';
}

export interface Insight {
  type: 'performance' | 'behavior' | 'anomaly' | 'recommendation';
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high';
  actionable: boolean;
  data?: Record<string, any>;
}

// ===== API TYPES =====

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: ApiError;
  metadata?: ResponseMetadata;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
  timestamp: Date;
}

export interface ResponseMetadata {
  timestamp: Date;
  requestId: string;
  version: string;
  pagination?: PaginationInfo;
}

export interface PaginationInfo {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
  hasNext: boolean;
  hasPrevious: boolean;
}

// ===== REQUEST/RESPONSE TYPES =====

export interface CreatePersonaRequest {
  name: string;
  description: string;
  behaviorProfile: BehaviorProfile;
  demographics: Demographics;
  technicalProfile: TechnicalProfile;
}

export interface UpdatePersonaRequest extends Partial<CreatePersonaRequest> {
  isActive?: boolean;
}

export interface CreateCampaignRequest {
  name: string;
  description: string;
  targetUrl: string;
  personaIds: string[];
  simulationConfig: SimulationConfig;
  scheduledStart?: Date;
  scheduledEnd?: Date;
}

export interface UpdateCampaignRequest extends Partial<CreateCampaignRequest> {
  status?: CampaignStatus;
}

export interface StartCampaignRequest {
  campaignId: string;
  immediate?: boolean;
}

export interface StopCampaignRequest {
  campaignId: string;
  reason?: string;
}

export interface GetSessionsRequest {
  campaignId?: string;
  personaId?: string;
  status?: SessionStatus;
  startDate?: Date;
  endDate?: Date;
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface GetAnalyticsRequest {
  campaignId: string;
  startDate: Date;
  endDate: Date;
  granularity: TimePeriod['granularity'];
  metrics?: string[];
}

// ===== WEBSOCKET TYPES =====

export interface WebSocketMessage<T = any> {
  type: string;
  data: T;
  timestamp: Date;
  requestId?: string;
}

export interface SessionUpdateMessage {
  sessionId: string;
  status: SessionStatus;
  progress: number; // 0-100
  currentPage?: string;
  actionsCount: number;
  errorsCount: number;
}

export interface CampaignUpdateMessage {
  campaignId: string;
  status: CampaignStatus;
  activeSessions: number;
  completedSessions: number;
  totalSessions: number;
  progress: number; // 0-100
}

export interface AnalyticsUpdateMessage {
  campaignId: string;
  metrics: CampaignMetrics;
  trends: TrendData[];
  insights: Insight[];
}

// ===== UTILITY TYPES =====

export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;

export type StatusFilter<T extends { status: string }> = T['status'];

export type EntityId = string;

export type Timestamp = Date;

export type UUID = string;

// ===== CONSTANTS =====

export const API_VERSION = 'v1';
export const API_BASE_PATH = `/api/${API_VERSION}`;

export const WEBSOCKET_EVENTS = {
  SESSION_UPDATE: 'session_update',
  CAMPAIGN_UPDATE: 'campaign_update',
  ANALYTICS_UPDATE: 'analytics_update',
  ERROR: 'error',
} as const;

export const CAMPAIGN_STATUSES: CampaignStatus[] = [
  'draft',
  'scheduled',
  'running',
  'paused',
  'completed',
  'cancelled',
  'error',
];

export const SESSION_STATUSES: SessionStatus[] = [
  'pending',
  'running',
  'completed',
  'failed',
  'cancelled',
];

export const ACTION_TYPES: ActionType[] = [
  'click',
  'scroll',
  'hover',
  'focus',
  'blur',
  'input',
  'submit',
  'navigate',
  'resize',
  'keypress',
  'mousemove',
  'mousedown',
  'mouseup',
];
