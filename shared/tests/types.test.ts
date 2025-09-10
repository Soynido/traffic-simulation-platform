// Tests unitaires pour les types partagés
// Ces tests vérifient que les types sont correctement définis et exportés

import { describe, it, expect } from 'vitest';
import type {
  Persona,
  Campaign,
  Session,
  BehaviorProfile,
  Demographics,
  TechnicalProfile,
  SimulationConfig,
  CreatePersonaRequest,
  CreateCampaignRequest,
  ApiResponse,
  WebSocketMessage,
} from '../types';
import {
  CAMPAIGN_STATUS,
  SESSION_STATUS,
  ACTION_TYPE,
  API_VERSION,
  WEBSOCKET_EVENTS,
} from '../constants';

describe('Types Partagés', () => {
  describe('Persona Types', () => {
    it('devrait définir correctement le type Persona', () => {
      const persona: Persona = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        name: 'Test Persona',
        description: 'A test persona for unit testing',
        behaviorProfile: {
          browsingSpeed: 'normal',
          clickPattern: 'systematic',
          scrollBehavior: 'smooth',
          sessionDuration: { min: 5, max: 30 },
          pageViewsPerSession: { min: 3, max: 10 },
          timeOnPage: { min: 10, max: 120 },
        },
        demographics: {
          age: { min: 25, max: 45 },
          gender: 'prefer_not_to_say',
          location: { country: 'US' },
          interests: ['technology'],
        },
        technicalProfile: {
          deviceTypes: [{ type: 'desktop', probability: 1.0 }],
          browsers: [{ name: 'Chrome', version: '120', userAgent: '', probability: 1.0 }],
          operatingSystems: [{ name: 'Windows', version: '10', probability: 1.0 }],
          screenResolutions: [{ width: 1920, height: 1080, probability: 1.0 }],
          connectionTypes: [{ type: 'wifi', speed: 'fast', probability: 1.0 }],
          timezone: 'UTC',
        },
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      expect(persona.id).toBeDefined();
      expect(persona.name).toBe('Test Persona');
      expect(persona.behaviorProfile).toBeDefined();
      expect(persona.demographics).toBeDefined();
      expect(persona.technicalProfile).toBeDefined();
      expect(persona.isActive).toBe(true);
    });

    it('devrait définir correctement le type BehaviorProfile', () => {
      const behaviorProfile: BehaviorProfile = {
        browsingSpeed: 'fast',
        clickPattern: 'random',
        scrollBehavior: 'jumpy',
        sessionDuration: { min: 10, max: 60 },
        pageViewsPerSession: { min: 5, max: 20 },
        timeOnPage: { min: 5, max: 300 },
      };

      expect(behaviorProfile.browsingSpeed).toBe('fast');
      expect(behaviorProfile.clickPattern).toBe('random');
      expect(behaviorProfile.scrollBehavior).toBe('jumpy');
      expect(behaviorProfile.sessionDuration.min).toBe(10);
      expect(behaviorProfile.sessionDuration.max).toBe(60);
    });

    it('devrait définir correctement le type Demographics', () => {
      const demographics: Demographics = {
        age: { min: 18, max: 65 },
        gender: 'male',
        location: { country: 'FR', region: 'Île-de-France', city: 'Paris' },
        interests: ['technology', 'gaming', 'sports'],
        occupation: 'Software Engineer',
      };

      expect(demographics.age.min).toBe(18);
      expect(demographics.age.max).toBe(65);
      expect(demographics.gender).toBe('male');
      expect(demographics.location.country).toBe('FR');
      expect(demographics.interests).toHaveLength(3);
    });

    it('devrait définir correctement le type TechnicalProfile', () => {
      const technicalProfile: TechnicalProfile = {
        deviceTypes: [
          { type: 'desktop', probability: 0.7 },
          { type: 'mobile', probability: 0.3 },
        ],
        browsers: [
          { name: 'Chrome', version: '120', userAgent: 'Mozilla/5.0...', probability: 0.8 },
          { name: 'Firefox', version: '119', userAgent: 'Mozilla/5.0...', probability: 0.2 },
        ],
        operatingSystems: [
          { name: 'Windows', version: '10', probability: 0.6 },
          { name: 'macOS', version: '14', probability: 0.4 },
        ],
        screenResolutions: [
          { width: 1920, height: 1080, probability: 0.5 },
          { width: 1366, height: 768, probability: 0.5 },
        ],
        connectionTypes: [
          { type: 'wifi', speed: 'fast', probability: 0.8 },
          { type: 'ethernet', speed: 'fast', probability: 0.2 },
        ],
        timezone: 'Europe/Paris',
      };

      expect(technicalProfile.deviceTypes).toHaveLength(2);
      expect(technicalProfile.browsers).toHaveLength(2);
      expect(technicalProfile.operatingSystems).toHaveLength(2);
      expect(technicalProfile.screenResolutions).toHaveLength(2);
      expect(technicalProfile.connectionTypes).toHaveLength(2);
      expect(technicalProfile.timezone).toBe('Europe/Paris');
    });
  });

  describe('Campaign Types', () => {
    it('devrait définir correctement le type Campaign', () => {
      const campaign: Campaign = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        name: 'Test Campaign',
        description: 'A test campaign for unit testing',
        targetUrl: 'https://example.com',
        personaIds: ['123e4567-e89b-12d3-a456-426614174001'],
        simulationConfig: {
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
        status: 'draft',
        metrics: {
          totalSessions: 0,
          completedSessions: 0,
          failedSessions: 0,
          averageSessionDuration: 0,
          totalPageViews: 0,
          uniquePageViews: 0,
          bounceRate: 0,
          conversionRate: 0,
        },
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      expect(campaign.id).toBeDefined();
      expect(campaign.name).toBe('Test Campaign');
      expect(campaign.targetUrl).toBe('https://example.com');
      expect(campaign.personaIds).toHaveLength(1);
      expect(campaign.simulationConfig).toBeDefined();
      expect(campaign.status).toBe('draft');
      expect(campaign.metrics).toBeDefined();
    });

    it('devrait définir correctement le type SimulationConfig', () => {
      const simulationConfig: SimulationConfig = {
        concurrentSessions: 10,
        sessionInterval: 60,
        duration: 120,
        randomization: {
          enabled: true,
          timeVariation: 0.2,
          actionVariation: 0.15,
          pathVariation: 0.25,
        },
        behaviorVariation: 0.2,
      };

      expect(simulationConfig.concurrentSessions).toBe(10);
      expect(simulationConfig.sessionInterval).toBe(60);
      expect(simulationConfig.duration).toBe(120);
      expect(simulationConfig.randomization.enabled).toBe(true);
      expect(simulationConfig.behaviorVariation).toBe(0.2);
    });
  });

  describe('Session Types', () => {
    it('devrait définir correctement le type Session', () => {
      const session: Session = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        campaignId: '123e4567-e89b-12d3-a456-426614174001',
        personaId: '123e4567-e89b-12d3-a456-426614174002',
        sessionId: 'session_1234567890_abc123',
        status: 'pending',
        startTime: new Date(),
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        ipAddress: '192.168.1.1',
        pageVisits: [],
        actions: [],
        metrics: {
          totalPageViews: 0,
          totalActions: 0,
          averageTimeOnPage: 0,
          bounceRate: 0,
          scrollDepth: 0,
          clickThroughRate: 0,
          formInteractions: 0,
          errorCount: 0,
        },
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      expect(session.id).toBeDefined();
      expect(session.campaignId).toBeDefined();
      expect(session.personaId).toBeDefined();
      expect(session.sessionId).toBe('session_1234567890_abc123');
      expect(session.status).toBe('pending');
      expect(session.userAgent).toBeDefined();
      expect(session.ipAddress).toBe('192.168.1.1');
      expect(session.pageVisits).toHaveLength(0);
      expect(session.actions).toHaveLength(0);
      expect(session.metrics).toBeDefined();
    });
  });

  describe('Request Types', () => {
    it('devrait définir correctement le type CreatePersonaRequest', () => {
      const createPersonaRequest: CreatePersonaRequest = {
        name: 'New Persona',
        description: 'A new persona for testing',
        behaviorProfile: {
          browsingSpeed: 'normal',
          clickPattern: 'systematic',
          scrollBehavior: 'smooth',
          sessionDuration: { min: 5, max: 30 },
          pageViewsPerSession: { min: 3, max: 10 },
          timeOnPage: { min: 10, max: 120 },
        },
        demographics: {
          age: { min: 25, max: 45 },
          gender: 'prefer_not_to_say',
          location: { country: 'US' },
          interests: ['technology'],
        },
        technicalProfile: {
          deviceTypes: [{ type: 'desktop', probability: 1.0 }],
          browsers: [{ name: 'Chrome', version: '120', userAgent: '', probability: 1.0 }],
          operatingSystems: [{ name: 'Windows', version: '10', probability: 1.0 }],
          screenResolutions: [{ width: 1920, height: 1080, probability: 1.0 }],
          connectionTypes: [{ type: 'wifi', speed: 'fast', probability: 1.0 }],
          timezone: 'UTC',
        },
      };

      expect(createPersonaRequest.name).toBe('New Persona');
      expect(createPersonaRequest.description).toBe('A new persona for testing');
      expect(createPersonaRequest.behaviorProfile).toBeDefined();
      expect(createPersonaRequest.demographics).toBeDefined();
      expect(createPersonaRequest.technicalProfile).toBeDefined();
    });

    it('devrait définir correctement le type CreateCampaignRequest', () => {
      const createCampaignRequest: CreateCampaignRequest = {
        name: 'New Campaign',
        description: 'A new campaign for testing',
        targetUrl: 'https://example.com',
        personaIds: ['123e4567-e89b-12d3-a456-426614174000'],
        simulationConfig: {
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
      };

      expect(createCampaignRequest.name).toBe('New Campaign');
      expect(createCampaignRequest.targetUrl).toBe('https://example.com');
      expect(createCampaignRequest.personaIds).toHaveLength(1);
      expect(createCampaignRequest.simulationConfig).toBeDefined();
    });
  });

  describe('API Types', () => {
    it('devrait définir correctement le type ApiResponse', () => {
      const apiResponse: ApiResponse<Persona> = {
        success: true,
        data: {
          id: '123e4567-e89b-12d3-a456-426614174000',
          name: 'Test Persona',
          description: 'A test persona',
          behaviorProfile: {
            browsingSpeed: 'normal',
            clickPattern: 'systematic',
            scrollBehavior: 'smooth',
            sessionDuration: { min: 5, max: 30 },
            pageViewsPerSession: { min: 3, max: 10 },
            timeOnPage: { min: 10, max: 120 },
          },
          demographics: {
            age: { min: 25, max: 45 },
            gender: 'prefer_not_to_say',
            location: { country: 'US' },
            interests: ['technology'],
          },
          technicalProfile: {
            deviceTypes: [{ type: 'desktop', probability: 1.0 }],
            browsers: [{ name: 'Chrome', version: '120', userAgent: '', probability: 1.0 }],
            operatingSystems: [{ name: 'Windows', version: '10', probability: 1.0 }],
            screenResolutions: [{ width: 1920, height: 1080, probability: 1.0 }],
            connectionTypes: [{ type: 'wifi', speed: 'fast', probability: 1.0 }],
            timezone: 'UTC',
          },
          isActive: true,
          createdAt: new Date(),
          updatedAt: new Date(),
        },
        metadata: {
          timestamp: new Date(),
          requestId: '123e4567-e89b-12d3-a456-426614174000',
          version: 'v1',
        },
      };

      expect(apiResponse.success).toBe(true);
      expect(apiResponse.data).toBeDefined();
      expect(apiResponse.metadata).toBeDefined();
    });

    it('devrait définir correctement le type WebSocketMessage', () => {
      const websocketMessage: WebSocketMessage<{ sessionId: string; status: string }> = {
        type: 'session_update',
        data: {
          sessionId: 'session_1234567890_abc123',
          status: 'running',
        },
        timestamp: new Date(),
        requestId: '123e4567-e89b-12d3-a456-426614174000',
      };

      expect(websocketMessage.type).toBe('session_update');
      expect(websocketMessage.data).toBeDefined();
      expect(websocketMessage.timestamp).toBeInstanceOf(Date);
      expect(websocketMessage.requestId).toBeDefined();
    });
  });

  describe('Constants', () => {
    it('devrait exporter les constantes de statut de campagne', () => {
      expect(CAMPAIGN_STATUS.DRAFT).toBe('draft');
      expect(CAMPAIGN_STATUS.RUNNING).toBe('running');
      expect(CAMPAIGN_STATUS.COMPLETED).toBe('completed');
    });

    it('devrait exporter les constantes de statut de session', () => {
      expect(SESSION_STATUS.PENDING).toBe('pending');
      expect(SESSION_STATUS.RUNNING).toBe('running');
      expect(SESSION_STATUS.COMPLETED).toBe('completed');
    });

    it('devrait exporter les constantes de type d\'action', () => {
      expect(ACTION_TYPE.CLICK).toBe('click');
      expect(ACTION_TYPE.SCROLL).toBe('scroll');
      expect(ACTION_TYPE.HOVER).toBe('hover');
    });

    it('devrait exporter les constantes API', () => {
      expect(API_VERSION).toBe('v1');
    });

    it('devrait exporter les constantes WebSocket', () => {
      expect(WEBSOCKET_EVENTS.SESSION_UPDATE).toBe('session_update');
      expect(WEBSOCKET_EVENTS.CAMPAIGN_UPDATE).toBe('campaign_update');
      expect(WEBSOCKET_EVENTS.ANALYTICS_UPDATE).toBe('analytics_update');
    });
  });
});
