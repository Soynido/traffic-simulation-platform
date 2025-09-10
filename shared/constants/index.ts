// Constantes partagées entre frontend et backend
// Ces constantes définissent les valeurs fixes utilisées dans l'application

// ===== API CONSTANTS =====
export const API_VERSION = 'v1';
export const API_BASE_PATH = `/api/${API_VERSION}`;

// ===== HTTP STATUS CODES =====
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_SERVER_ERROR: 500,
  BAD_GATEWAY: 502,
  SERVICE_UNAVAILABLE: 503,
  GATEWAY_TIMEOUT: 504,
} as const;

// ===== ERROR CODES =====
export const ERROR_CODES = {
  // Validation errors
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  INVALID_INPUT: 'INVALID_INPUT',
  MISSING_REQUIRED_FIELD: 'MISSING_REQUIRED_FIELD',
  INVALID_FORMAT: 'INVALID_FORMAT',
  
  // Authentication errors
  UNAUTHORIZED: 'UNAUTHORIZED',
  INVALID_TOKEN: 'INVALID_TOKEN',
  TOKEN_EXPIRED: 'TOKEN_EXPIRED',
  INSUFFICIENT_PERMISSIONS: 'INSUFFICIENT_PERMISSIONS',
  
  // Resource errors
  RESOURCE_NOT_FOUND: 'RESOURCE_NOT_FOUND',
  RESOURCE_ALREADY_EXISTS: 'RESOURCE_ALREADY_EXISTS',
  RESOURCE_CONFLICT: 'RESOURCE_CONFLICT',
  RESOURCE_LOCKED: 'RESOURCE_LOCKED',
  
  // Business logic errors
  CAMPAIGN_NOT_ACTIVE: 'CAMPAIGN_NOT_ACTIVE',
  CAMPAIGN_ALREADY_RUNNING: 'CAMPAIGN_ALREADY_RUNNING',
  CAMPAIGN_NOT_SCHEDULED: 'CAMPAIGN_NOT_SCHEDULED',
  SESSION_NOT_FOUND: 'SESSION_NOT_FOUND',
  SESSION_ALREADY_COMPLETED: 'SESSION_ALREADY_COMPLETED',
  PERSONA_NOT_ACTIVE: 'PERSONA_NOT_ACTIVE',
  
  // System errors
  DATABASE_ERROR: 'DATABASE_ERROR',
  REDIS_ERROR: 'REDIS_ERROR',
  EXTERNAL_SERVICE_ERROR: 'EXTERNAL_SERVICE_ERROR',
  SIMULATION_ENGINE_ERROR: 'SIMULATION_ENGINE_ERROR',
  BROWSER_ERROR: 'BROWSER_ERROR',
  
  // Rate limiting
  RATE_LIMIT_EXCEEDED: 'RATE_LIMIT_EXCEEDED',
  TOO_MANY_CONCURRENT_SESSIONS: 'TOO_MANY_CONCURRENT_SESSIONS',
  
  // WebSocket errors
  WEBSOCKET_CONNECTION_ERROR: 'WEBSOCKET_CONNECTION_ERROR',
  WEBSOCKET_AUTHENTICATION_ERROR: 'WEBSOCKET_AUTHENTICATION_ERROR',
  WEBSOCKET_SUBSCRIPTION_ERROR: 'WEBSOCKET_SUBSCRIPTION_ERROR',
} as const;

// ===== CAMPAIGN STATUSES =====
export const CAMPAIGN_STATUS = {
  DRAFT: 'draft',
  SCHEDULED: 'scheduled',
  RUNNING: 'running',
  PAUSED: 'paused',
  COMPLETED: 'completed',
  CANCELLED: 'cancelled',
  ERROR: 'error',
} as const;

// ===== SESSION STATUSES =====
export const SESSION_STATUS = {
  PENDING: 'pending',
  RUNNING: 'running',
  COMPLETED: 'completed',
  FAILED: 'failed',
  CANCELLED: 'cancelled',
} as const;

// ===== ACTION TYPES =====
export const ACTION_TYPE = {
  CLICK: 'click',
  SCROLL: 'scroll',
  HOVER: 'hover',
  FOCUS: 'focus',
  BLUR: 'blur',
  INPUT: 'input',
  SUBMIT: 'submit',
  NAVIGATE: 'navigate',
  RESIZE: 'resize',
  KEYPRESS: 'keypress',
  MOUSEMOVE: 'mousemove',
  MOUSEDOWN: 'mousedown',
  MOUSEUP: 'mouseup',
} as const;

// ===== BROWSER TYPES =====
export const BROWSER_TYPE = {
  CHROME: 'chrome',
  FIREFOX: 'firefox',
  SAFARI: 'safari',
  EDGE: 'edge',
  OPERA: 'opera',
} as const;

// ===== DEVICE TYPES =====
export const DEVICE_TYPE = {
  DESKTOP: 'desktop',
  MOBILE: 'mobile',
  TABLET: 'tablet',
} as const;

// ===== CONNECTION TYPES =====
export const CONNECTION_TYPE = {
  WIFI: 'wifi',
  ETHERNET: 'ethernet',
  MOBILE_3G: '3g',
  MOBILE_4G: '4g',
  MOBILE_5G: '5g',
} as const;

// ===== CONNECTION SPEEDS =====
export const CONNECTION_SPEED = {
  SLOW: 'slow',
  MEDIUM: 'medium',
  FAST: 'fast',
} as const;

// ===== BROWSING SPEEDS =====
export const BROWSING_SPEED = {
  SLOW: 'slow',
  NORMAL: 'normal',
  FAST: 'fast',
} as const;

// ===== CLICK PATTERNS =====
export const CLICK_PATTERN = {
  RANDOM: 'random',
  SYSTEMATIC: 'systematic',
  HESITANT: 'hesitant',
} as const;

// ===== SCROLL BEHAVIORS =====
export const SCROLL_BEHAVIOR = {
  SMOOTH: 'smooth',
  JUMPY: 'jumpy',
  MINIMAL: 'minimal',
} as const;

// ===== WEBSOCKET EVENTS =====
export const WEBSOCKET_EVENTS = {
  SESSION_UPDATE: 'session_update',
  CAMPAIGN_UPDATE: 'campaign_update',
  ANALYTICS_UPDATE: 'analytics_update',
  ERROR: 'error',
  CONNECTION_ESTABLISHED: 'connection_established',
  CONNECTION_LOST: 'connection_lost',
  HEARTBEAT: 'heartbeat',
} as const;

// ===== PAGINATION =====
export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_LIMIT: 20,
  MAX_LIMIT: 1000,
  MIN_LIMIT: 1,
} as const;

// ===== TIME CONSTANTS =====
export const TIME = {
  SECOND: 1000,
  MINUTE: 60 * 1000,
  HOUR: 60 * 60 * 1000,
  DAY: 24 * 60 * 60 * 1000,
  WEEK: 7 * 24 * 60 * 60 * 1000,
  MONTH: 30 * 24 * 60 * 60 * 1000,
} as const;

// ===== SIMULATION CONSTANTS =====
export const SIMULATION = {
  MAX_CONCURRENT_SESSIONS: 100,
  MIN_CONCURRENT_SESSIONS: 1,
  MAX_SESSION_DURATION: 1440, // 24 hours in minutes
  MIN_SESSION_DURATION: 1, // 1 minute
  MAX_SESSION_INTERVAL: 3600, // 1 hour in seconds
  MIN_SESSION_INTERVAL: 1, // 1 second
  MAX_CAMPAIGN_DURATION: 10080, // 1 week in minutes
  MIN_CAMPAIGN_DURATION: 1, // 1 minute
  DEFAULT_BEHAVIOR_VARIATION: 0.1, // 10%
  MAX_BEHAVIOR_VARIATION: 1.0, // 100%
  MIN_BEHAVIOR_VARIATION: 0.0, // 0%
} as const;

// ===== BROWSER CONSTANTS =====
export const BROWSER = {
  DEFAULT_VIEWPORT: {
    width: 1920,
    height: 1080,
  },
  MOBILE_VIEWPORT: {
    width: 375,
    height: 667,
  },
  TABLET_VIEWPORT: {
    width: 768,
    height: 1024,
  },
  DEFAULT_USER_AGENT: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  HEADLESS: true,
  TIMEOUT: 30000, // 30 seconds
  NAVIGATION_TIMEOUT: 60000, // 1 minute
} as const;

// ===== REDIS CONSTANTS =====
export const REDIS = {
  SESSION_PREFIX: 'session:',
  CAMPAIGN_PREFIX: 'campaign:',
  PERSONA_PREFIX: 'persona:',
  QUEUE_PREFIX: 'queue:',
  CACHE_PREFIX: 'cache:',
  LOCK_PREFIX: 'lock:',
  DEFAULT_TTL: 3600, // 1 hour
  SESSION_TTL: 86400, // 24 hours
  CACHE_TTL: 1800, // 30 minutes
} as const;

// ===== DATABASE CONSTANTS =====
export const DATABASE = {
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 1000,
  DEFAULT_ORDER: 'createdAt',
  DEFAULT_ORDER_DIRECTION: 'DESC',
} as const;

// ===== VALIDATION CONSTANTS =====
export const VALIDATION = {
  MIN_NAME_LENGTH: 1,
  MAX_NAME_LENGTH: 100,
  MIN_DESCRIPTION_LENGTH: 1,
  MAX_DESCRIPTION_LENGTH: 1000,
  MIN_URL_LENGTH: 1,
  MAX_URL_LENGTH: 2048,
  MIN_AGE: 13,
  MAX_AGE: 100,
  MIN_INTERESTS: 1,
  MAX_INTERESTS: 20,
  MIN_PERSONA_IDS: 1,
  MAX_PERSONA_IDS: 50,
  MIN_CONCURRENT_SESSIONS: 1,
  MAX_CONCURRENT_SESSIONS: 100,
  MIN_SESSION_DURATION: 1,
  MAX_SESSION_DURATION: 1440,
  MIN_SESSION_INTERVAL: 1,
  MAX_SESSION_INTERVAL: 3600,
  MIN_CAMPAIGN_DURATION: 1,
  MAX_CAMPAIGN_DURATION: 10080,
} as const;

// ===== ANALYTICS CONSTANTS =====
export const ANALYTICS = {
  GRANULARITY: {
    MINUTE: 'minute',
    HOUR: 'hour',
    DAY: 'day',
    WEEK: 'week',
    MONTH: 'month',
  },
  METRICS: {
    SESSIONS: 'sessions',
    PAGE_VIEWS: 'page_views',
    UNIQUE_PAGE_VIEWS: 'unique_page_views',
    BOUNCE_RATE: 'bounce_rate',
    AVERAGE_SESSION_DURATION: 'average_session_duration',
    CONVERSION_RATE: 'conversion_rate',
    CLICK_THROUGH_RATE: 'click_through_rate',
    SCROLL_DEPTH: 'scroll_depth',
  },
  INSIGHT_TYPES: {
    PERFORMANCE: 'performance',
    BEHAVIOR: 'behavior',
    ANOMALY: 'anomaly',
    RECOMMENDATION: 'recommendation',
  },
  INSIGHT_SEVERITY: {
    LOW: 'low',
    MEDIUM: 'medium',
    HIGH: 'high',
  },
} as const;

// ===== LOGGING CONSTANTS =====
export const LOGGING = {
  LEVELS: {
    ERROR: 'error',
    WARN: 'warn',
    INFO: 'info',
    DEBUG: 'debug',
  },
  CONTEXTS: {
    API: 'api',
    SIMULATION: 'simulation',
    DATABASE: 'database',
    REDIS: 'redis',
    WEBSOCKET: 'websocket',
    BROWSER: 'browser',
  },
} as const;

// ===== RATE LIMITING =====
export const RATE_LIMITING = {
  API_REQUESTS_PER_MINUTE: 100,
  API_REQUESTS_PER_HOUR: 1000,
  WEBSOCKET_CONNECTIONS_PER_IP: 10,
  SIMULATION_REQUESTS_PER_HOUR: 50,
  MAX_CONCURRENT_SIMULATIONS: 10,
} as const;

// ===== SECURITY CONSTANTS =====
export const SECURITY = {
  JWT_EXPIRATION: '24h',
  REFRESH_TOKEN_EXPIRATION: '7d',
  PASSWORD_MIN_LENGTH: 8,
  PASSWORD_MAX_LENGTH: 128,
  SESSION_TIMEOUT: 30 * 60 * 1000, // 30 minutes
  MAX_LOGIN_ATTEMPTS: 5,
  LOCKOUT_DURATION: 15 * 60 * 1000, // 15 minutes
} as const;

// ===== ENVIRONMENT CONSTANTS =====
export const ENVIRONMENT = {
  DEVELOPMENT: 'development',
  STAGING: 'staging',
  PRODUCTION: 'production',
  TEST: 'test',
} as const;

// ===== FEATURE FLAGS =====
export const FEATURE_FLAGS = {
  ENABLE_WEBSOCKETS: 'enable_websockets',
  ENABLE_ANALYTICS: 'enable_analytics',
  ENABLE_SIMULATION: 'enable_simulation',
  ENABLE_RATE_LIMITING: 'enable_rate_limiting',
  ENABLE_CACHING: 'enable_caching',
  ENABLE_LOGGING: 'enable_logging',
} as const;

// ===== DEFAULT VALUES =====
export const DEFAULTS = {
  PERSONA: {
    BEHAVIOR_PROFILE: {
      browsingSpeed: 'normal',
      clickPattern: 'systematic',
      scrollBehavior: 'smooth',
      sessionDuration: { min: 5, max: 30 },
      pageViewsPerSession: { min: 3, max: 10 },
      timeOnPage: { min: 10, max: 120 },
    },
    DEMOGRAPHICS: {
      age: { min: 25, max: 45 },
      gender: 'prefer_not_to_say',
      location: { country: 'US' },
      interests: ['technology'],
    },
    TECHNICAL_PROFILE: {
      deviceTypes: [{ type: 'desktop', probability: 1.0 }],
      browsers: [{ name: 'Chrome', version: '120', userAgent: '', probability: 1.0 }],
      operatingSystems: [{ name: 'Windows', version: '10', probability: 1.0 }],
      screenResolutions: [{ width: 1920, height: 1080, probability: 1.0 }],
      connectionTypes: [{ type: 'wifi', speed: 'fast', probability: 1.0 }],
      timezone: 'UTC',
    },
  },
  CAMPAIGN: {
    SIMULATION_CONFIG: {
      concurrentSessions: 5,
      sessionInterval: 30,
      duration: 60,
      randomization: {
        enabled: true,
        timeVariation: 0.1,
        actionVariation: 0.1,
        pathVariation: 0.1,
      },
      behaviorVariation: 0.1,
    },
  },
  SESSION: {
    TIMEOUT: 30000, // 30 seconds
    MAX_DURATION: 3600, // 1 hour
    MAX_PAGE_VISITS: 100,
    MAX_ACTIONS: 1000,
  },
} as const;

// ===== EXPORT ALL CONSTANTS =====
export {
  // API
  API_VERSION,
  API_BASE_PATH,
  
  // HTTP
  HTTP_STATUS,
  
  // Errors
  ERROR_CODES,
  
  // Statuses
  CAMPAIGN_STATUS,
  SESSION_STATUS,
  
  // Types
  ACTION_TYPE,
  BROWSER_TYPE,
  DEVICE_TYPE,
  CONNECTION_TYPE,
  CONNECTION_SPEED,
  BROWSING_SPEED,
  CLICK_PATTERN,
  SCROLL_BEHAVIOR,
  
  // WebSocket
  WEBSOCKET_EVENTS,
  
  // Pagination
  PAGINATION,
  
  // Time
  TIME,
  
  // Simulation
  SIMULATION,
  
  // Browser
  BROWSER,
  
  // Redis
  REDIS,
  
  // Database
  DATABASE,
  
  // Validation
  VALIDATION,
  
  // Analytics
  ANALYTICS,
  
  // Logging
  LOGGING,
  
  // Rate limiting
  RATE_LIMITING,
  
  // Security
  SECURITY,
  
  // Environment
  ENVIRONMENT,
  
  // Feature flags
  FEATURE_FLAGS,
  
  // Defaults
  DEFAULTS,
};
