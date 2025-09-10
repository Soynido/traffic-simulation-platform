// Schémas de validation partagés (Zod)
// Ces schémas définissent la validation des données côté frontend et backend

import { z } from 'zod';
import type {
  BehaviorProfile,
  Demographics,
  TechnicalProfile,
  SimulationConfig,
  RandomizationConfig,
  CreatePersonaRequest,
  UpdatePersonaRequest,
  CreateCampaignRequest,
  UpdateCampaignRequest,
  GetSessionsRequest,
  GetAnalyticsRequest,
} from '../types';

// ===== SCHEMAS DE BASE =====

export const BaseEntitySchema = z.object({
  id: z.string().uuid(),
  createdAt: z.date(),
  updatedAt: z.date(),
});

export const CoordinatesSchema = z.object({
  x: z.number().min(0),
  y: z.number().min(0),
});

export const ViewportSizeSchema = z.object({
  width: z.number().min(1),
  height: z.number().min(1),
});

// ===== PERSONA SCHEMAS =====

export const BehaviorProfileSchema: z.ZodType<BehaviorProfile> = z.object({
  browsingSpeed: z.enum(['slow', 'normal', 'fast']),
  clickPattern: z.enum(['random', 'systematic', 'hesitant']),
  scrollBehavior: z.enum(['smooth', 'jumpy', 'minimal']),
  sessionDuration: z.object({
    min: z.number().min(1).max(1440), // 1 minute to 24 hours
    max: z.number().min(1).max(1440),
  }).refine(data => data.max >= data.min, {
    message: "Max duration must be greater than or equal to min duration",
  }),
  pageViewsPerSession: z.object({
    min: z.number().min(1).max(1000),
    max: z.number().min(1).max(1000),
  }).refine(data => data.max >= data.min, {
    message: "Max page views must be greater than or equal to min page views",
  }),
  timeOnPage: z.object({
    min: z.number().min(1).max(3600), // 1 second to 1 hour
    max: z.number().min(1).max(3600),
  }).refine(data => data.max >= data.min, {
    message: "Max time on page must be greater than or equal to min time on page",
  }),
});

export const DemographicsSchema: z.ZodType<Demographics> = z.object({
  age: z.object({
    min: z.number().min(13).max(100),
    max: z.number().min(13).max(100),
  }).refine(data => data.max >= data.min, {
    message: "Max age must be greater than or equal to min age",
  }),
  gender: z.enum(['male', 'female', 'other', 'prefer_not_to_say']),
  location: z.object({
    country: z.string().min(2).max(100),
    region: z.string().min(2).max(100).optional(),
    city: z.string().min(2).max(100).optional(),
  }),
  interests: z.array(z.string().min(1).max(100)).min(1).max(20),
  occupation: z.string().min(1).max(100).optional(),
});

export const DeviceTypeSchema = z.object({
  type: z.enum(['desktop', 'mobile', 'tablet']),
  probability: z.number().min(0).max(1),
});

export const BrowserInfoSchema = z.object({
  name: z.string().min(1).max(50),
  version: z.string().min(1).max(20),
  userAgent: z.string().min(1).max(500),
  probability: z.number().min(0).max(1),
});

export const OSInfoSchema = z.object({
  name: z.string().min(1).max(50),
  version: z.string().min(1).max(20),
  probability: z.number().min(0).max(1),
});

export const ScreenResolutionSchema = z.object({
  width: z.number().min(320).max(7680), // Mobile to 8K
  height: z.number().min(240).max(4320),
  probability: z.number().min(0).max(1),
});

export const ConnectionTypeSchema = z.object({
  type: z.enum(['wifi', '4g', '5g', 'ethernet', '3g']),
  speed: z.enum(['slow', 'medium', 'fast']),
  probability: z.number().min(0).max(1),
});

export const TechnicalProfileSchema: z.ZodType<TechnicalProfile> = z.object({
  deviceTypes: z.array(DeviceTypeSchema).min(1).max(10),
  browsers: z.array(BrowserInfoSchema).min(1).max(20),
  operatingSystems: z.array(OSInfoSchema).min(1).max(10),
  screenResolutions: z.array(ScreenResolutionSchema).min(1).max(20),
  connectionTypes: z.array(ConnectionTypeSchema).min(1).max(10),
  timezone: z.string().min(1).max(50),
}).refine(data => {
  const totalDeviceProbability = data.deviceTypes.reduce((sum, device) => sum + device.probability, 0);
  const totalBrowserProbability = data.browsers.reduce((sum, browser) => sum + browser.probability, 0);
  const totalOSProbability = data.operatingSystems.reduce((sum, os) => sum + os.probability, 0);
  const totalResolutionProbability = data.screenResolutions.reduce((sum, res) => sum + res.probability, 0);
  const totalConnectionProbability = data.connectionTypes.reduce((sum, conn) => sum + conn.probability, 0);
  
  return Math.abs(totalDeviceProbability - 1) < 0.01 &&
         Math.abs(totalBrowserProbability - 1) < 0.01 &&
         Math.abs(totalOSProbability - 1) < 0.01 &&
         Math.abs(totalResolutionProbability - 1) < 0.01 &&
         Math.abs(totalConnectionProbability - 1) < 0.01;
}, {
  message: "All probability arrays must sum to 1.0",
});

export const PersonaSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1).max(100),
  description: z.string().min(1).max(1000),
  behaviorProfile: BehaviorProfileSchema,
  demographics: DemographicsSchema,
  technicalProfile: TechnicalProfileSchema,
  isActive: z.boolean(),
  createdAt: z.date(),
  updatedAt: z.date(),
});

// ===== CAMPAIGN SCHEMAS =====

export const RandomizationConfigSchema: z.ZodType<RandomizationConfig> = z.object({
  enabled: z.boolean(),
  timeVariation: z.number().min(0).max(1),
  actionVariation: z.number().min(0).max(1),
  pathVariation: z.number().min(0).max(1),
});

export const SimulationConfigSchema: z.ZodType<SimulationConfig> = z.object({
  concurrentSessions: z.number().min(1).max(100),
  sessionInterval: z.number().min(1).max(3600), // 1 second to 1 hour
  duration: z.number().min(1).max(10080), // 1 minute to 1 week
  randomization: RandomizationConfigSchema,
  behaviorVariation: z.number().min(0).max(1),
});

export const CampaignStatusSchema = z.enum([
  'draft',
  'scheduled',
  'running',
  'paused',
  'completed',
  'cancelled',
  'error',
]);

export const CampaignMetricsSchema = z.object({
  totalSessions: z.number().min(0),
  completedSessions: z.number().min(0),
  failedSessions: z.number().min(0),
  averageSessionDuration: z.number().min(0),
  totalPageViews: z.number().min(0),
  uniquePageViews: z.number().min(0),
  bounceRate: z.number().min(0).max(1),
  conversionRate: z.number().min(0).max(1),
});

export const CampaignSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1).max(100),
  description: z.string().min(1).max(1000),
  targetUrl: z.string().url(),
  personaIds: z.array(z.string().uuid()).min(1).max(50),
  simulationConfig: SimulationConfigSchema,
  status: CampaignStatusSchema,
  scheduledStart: z.date().optional(),
  scheduledEnd: z.date().optional(),
  actualStart: z.date().optional(),
  actualEnd: z.date().optional(),
  metrics: CampaignMetricsSchema,
  createdAt: z.date(),
  updatedAt: z.date(),
});

// ===== SESSION SCHEMAS =====

export const SessionStatusSchema = z.enum([
  'pending',
  'running',
  'completed',
  'failed',
  'cancelled',
]);

export const ActionTypeSchema = z.enum([
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
]);

export const ElementInfoSchema = z.object({
  tagName: z.string().min(1).max(50),
  id: z.string().min(1).max(100).optional(),
  className: z.string().min(1).max(200).optional(),
  text: z.string().max(1000).optional(),
  attributes: z.record(z.string(), z.string()).optional(),
});

export const ActionSchema = z.object({
  id: z.string().uuid(),
  sessionId: z.string().uuid(),
  pageVisitId: z.string().uuid().optional(),
  type: ActionTypeSchema,
  timestamp: z.date(),
  coordinates: CoordinatesSchema.optional(),
  element: ElementInfoSchema.optional(),
  data: z.record(z.string(), z.any()).optional(),
  duration: z.number().min(0).max(60000).optional(), // max 1 minute
  createdAt: z.date(),
  updatedAt: z.date(),
});

export const PageVisitSchema = z.object({
  id: z.string().uuid(),
  sessionId: z.string().uuid(),
  url: z.string().url(),
  title: z.string().min(1).max(200),
  timestamp: z.date(),
  duration: z.number().min(0).max(3600), // max 1 hour
  scrollDepth: z.number().min(0).max(1),
  viewportSize: ViewportSizeSchema,
  referrer: z.string().url().optional(),
  actions: z.array(ActionSchema),
  createdAt: z.date(),
  updatedAt: z.date(),
});

export const SessionMetricsSchema = z.object({
  totalPageViews: z.number().min(0),
  totalActions: z.number().min(0),
  averageTimeOnPage: z.number().min(0),
  bounceRate: z.number().min(0).max(1),
  scrollDepth: z.number().min(0).max(1),
  clickThroughRate: z.number().min(0).max(1),
  formInteractions: z.number().min(0),
  errorCount: z.number().min(0),
});

export const SessionSchema = z.object({
  id: z.string().uuid(),
  campaignId: z.string().uuid(),
  personaId: z.string().uuid(),
  sessionId: z.string().min(1).max(100),
  status: SessionStatusSchema,
  startTime: z.date(),
  endTime: z.date().optional(),
  duration: z.number().min(0).optional(),
  userAgent: z.string().min(1).max(500),
  ipAddress: z.string().ip(),
  referrer: z.string().url().optional(),
  pageVisits: z.array(PageVisitSchema),
  actions: z.array(ActionSchema),
  metrics: SessionMetricsSchema,
  createdAt: z.date(),
  updatedAt: z.date(),
});

// ===== REQUEST/RESPONSE SCHEMAS =====

export const CreatePersonaRequestSchema: z.ZodType<CreatePersonaRequest> = z.object({
  name: z.string().min(1).max(100),
  description: z.string().min(1).max(1000),
  behaviorProfile: BehaviorProfileSchema,
  demographics: DemographicsSchema,
  technicalProfile: TechnicalProfileSchema,
});

export const UpdatePersonaRequestSchema: z.ZodType<UpdatePersonaRequest> = z.object({
  name: z.string().min(1).max(100).optional(),
  description: z.string().min(1).max(1000).optional(),
  behaviorProfile: BehaviorProfileSchema.optional(),
  demographics: DemographicsSchema.optional(),
  technicalProfile: TechnicalProfileSchema.optional(),
  isActive: z.boolean().optional(),
});

export const CreateCampaignRequestSchema: z.ZodType<CreateCampaignRequest> = z.object({
  name: z.string().min(1).max(100),
  description: z.string().min(1).max(1000),
  targetUrl: z.string().url(),
  personaIds: z.array(z.string().uuid()).min(1).max(50),
  simulationConfig: SimulationConfigSchema,
  scheduledStart: z.date().optional(),
  scheduledEnd: z.date().optional(),
});

export const UpdateCampaignRequestSchema: z.ZodType<UpdateCampaignRequest> = z.object({
  name: z.string().min(1).max(100).optional(),
  description: z.string().min(1).max(1000).optional(),
  targetUrl: z.string().url().optional(),
  personaIds: z.array(z.string().uuid()).min(1).max(50).optional(),
  simulationConfig: SimulationConfigSchema.optional(),
  scheduledStart: z.date().optional(),
  scheduledEnd: z.date().optional(),
  status: CampaignStatusSchema.optional(),
});

export const StartCampaignRequestSchema = z.object({
  campaignId: z.string().uuid(),
  immediate: z.boolean().optional(),
});

export const StopCampaignRequestSchema = z.object({
  campaignId: z.string().uuid(),
  reason: z.string().min(1).max(500).optional(),
});

export const GetSessionsRequestSchema: z.ZodType<GetSessionsRequest> = z.object({
  campaignId: z.string().uuid().optional(),
  personaId: z.string().uuid().optional(),
  status: SessionStatusSchema.optional(),
  startDate: z.date().optional(),
  endDate: z.date().optional(),
  page: z.number().min(1).max(10000).optional(),
  limit: z.number().min(1).max(1000).optional(),
  sortBy: z.string().min(1).max(50).optional(),
  sortOrder: z.enum(['asc', 'desc']).optional(),
});

export const GetAnalyticsRequestSchema: z.ZodType<GetAnalyticsRequest> = z.object({
  campaignId: z.string().uuid(),
  startDate: z.date(),
  endDate: z.date(),
  granularity: z.enum(['minute', 'hour', 'day', 'week', 'month']),
  metrics: z.array(z.string().min(1).max(50)).optional(),
}).refine(data => data.endDate > data.startDate, {
  message: "End date must be after start date",
});

// ===== API RESPONSE SCHEMAS =====

export const ApiErrorSchema = z.object({
  code: z.string().min(1).max(50),
  message: z.string().min(1).max(500),
  details: z.record(z.string(), z.any()).optional(),
  timestamp: z.date(),
});

export const PaginationInfoSchema = z.object({
  page: z.number().min(1),
  limit: z.number().min(1).max(1000),
  total: z.number().min(0),
  totalPages: z.number().min(0),
  hasNext: z.boolean(),
  hasPrevious: z.boolean(),
});

export const ResponseMetadataSchema = z.object({
  timestamp: z.date(),
  requestId: z.string().uuid(),
  version: z.string().min(1).max(20),
  pagination: PaginationInfoSchema.optional(),
});

export const ApiResponseSchema = <T extends z.ZodTypeAny>(dataSchema: T) =>
  z.object({
    success: z.boolean(),
    data: dataSchema.optional(),
    error: ApiErrorSchema.optional(),
    metadata: ResponseMetadataSchema.optional(),
  });

// ===== WEBSOCKET SCHEMAS =====

export const WebSocketMessageSchema = <T extends z.ZodTypeAny>(dataSchema: T) =>
  z.object({
    type: z.string().min(1).max(50),
    data: dataSchema,
    timestamp: z.date(),
    requestId: z.string().uuid().optional(),
  });

export const SessionUpdateMessageSchema = z.object({
  sessionId: z.string().uuid(),
  status: SessionStatusSchema,
  progress: z.number().min(0).max(100),
  currentPage: z.string().url().optional(),
  actionsCount: z.number().min(0),
  errorsCount: z.number().min(0),
});

export const CampaignUpdateMessageSchema = z.object({
  campaignId: z.string().uuid(),
  status: CampaignStatusSchema,
  activeSessions: z.number().min(0),
  completedSessions: z.number().min(0),
  totalSessions: z.number().min(0),
  progress: z.number().min(0).max(100),
});

// ===== VALIDATION HELPERS =====

export const validatePersona = (data: unknown) => PersonaSchema.parse(data);
export const validateCampaign = (data: unknown) => CampaignSchema.parse(data);
export const validateSession = (data: unknown) => SessionSchema.parse(data);
export const validateCreatePersonaRequest = (data: unknown) => CreatePersonaRequestSchema.parse(data);
export const validateUpdatePersonaRequest = (data: unknown) => UpdatePersonaRequestSchema.parse(data);
export const validateCreateCampaignRequest = (data: unknown) => CreateCampaignRequestSchema.parse(data);
export const validateUpdateCampaignRequest = (data: unknown) => UpdateCampaignRequestSchema.parse(data);
export const validateGetSessionsRequest = (data: unknown) => GetSessionsRequestSchema.parse(data);
export const validateGetAnalyticsRequest = (data: unknown) => GetAnalyticsRequestSchema.parse(data);

// ===== EXPORT ALL SCHEMAS =====

export {
  // Base schemas
  BaseEntitySchema,
  CoordinatesSchema,
  ViewportSizeSchema,
  
  // Persona schemas
  BehaviorProfileSchema,
  DemographicsSchema,
  TechnicalProfileSchema,
  DeviceTypeSchema,
  BrowserInfoSchema,
  OSInfoSchema,
  ScreenResolutionSchema,
  ConnectionTypeSchema,
  PersonaSchema,
  
  // Campaign schemas
  RandomizationConfigSchema,
  SimulationConfigSchema,
  CampaignStatusSchema,
  CampaignMetricsSchema,
  CampaignSchema,
  
  // Session schemas
  SessionStatusSchema,
  ActionTypeSchema,
  ElementInfoSchema,
  ActionSchema,
  PageVisitSchema,
  SessionMetricsSchema,
  SessionSchema,
  
  // Request/Response schemas
  CreatePersonaRequestSchema,
  UpdatePersonaRequestSchema,
  CreateCampaignRequestSchema,
  UpdateCampaignRequestSchema,
  StartCampaignRequestSchema,
  StopCampaignRequestSchema,
  GetSessionsRequestSchema,
  GetAnalyticsRequestSchema,
  
  // API schemas
  ApiErrorSchema,
  PaginationInfoSchema,
  ResponseMetadataSchema,
  ApiResponseSchema,
  
  // WebSocket schemas
  WebSocketMessageSchema,
  SessionUpdateMessageSchema,
  CampaignUpdateMessageSchema,
};
