// Tests unitaires pour les schémas de validation
// Ces tests vérifient que les schémas Zod valident correctement les données

import { describe, it, expect } from 'vitest';
import {
  PersonaSchema,
  CampaignSchema,
  SessionSchema,
  CreatePersonaRequestSchema,
  CreateCampaignRequestSchema,
  BehaviorProfileSchema,
  DemographicsSchema,
  TechnicalProfileSchema,
  SimulationConfigSchema,
  ApiResponseSchema,
  validatePersona,
  validateCampaign,
  validateCreatePersonaRequest,
  validateCreateCampaignRequest,
} from '../schemas';

describe('Schémas de Validation', () => {
  describe('PersonaSchema', () => {
    it('devrait valider un persona valide', () => {
      const validPersona = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        name: 'Test Persona',
        description: 'A test persona for validation',
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
          browsers: [{ name: 'Chrome', version: '120', userAgent: 'Mozilla/5.0...', probability: 1.0 }],
          operatingSystems: [{ name: 'Windows', version: '10', probability: 1.0 }],
          screenResolutions: [{ width: 1920, height: 1080, probability: 1.0 }],
          connectionTypes: [{ type: 'wifi', speed: 'fast', probability: 1.0 }],
          timezone: 'UTC',
        },
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      expect(() => PersonaSchema.parse(validPersona)).not.toThrow();
      expect(() => validatePersona(validPersona)).not.toThrow();
    });

    it('devrait rejeter un persona avec des données invalides', () => {
      const invalidPersona = {
        id: 'invalid-uuid',
        name: '',
        description: 'A test persona',
        behaviorProfile: {
          browsingSpeed: 'invalid',
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
          browsers: [{ name: 'Chrome', version: '120', userAgent: 'Mozilla/5.0...', probability: 1.0 }],
          operatingSystems: [{ name: 'Windows', version: '10', probability: 1.0 }],
          screenResolutions: [{ width: 1920, height: 1080, probability: 1.0 }],
          connectionTypes: [{ type: 'wifi', speed: 'fast', probability: 1.0 }],
          timezone: 'UTC',
        },
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      expect(() => PersonaSchema.parse(invalidPersona)).toThrow();
      expect(() => validatePersona(invalidPersona)).toThrow();
    });
  });

  describe('BehaviorProfileSchema', () => {
    it('devrait valider un profil de comportement valide', () => {
      const validBehaviorProfile = {
        browsingSpeed: 'fast',
        clickPattern: 'random',
        scrollBehavior: 'jumpy',
        sessionDuration: { min: 10, max: 60 },
        pageViewsPerSession: { min: 5, max: 20 },
        timeOnPage: { min: 5, max: 300 },
      };

      expect(() => BehaviorProfileSchema.parse(validBehaviorProfile)).not.toThrow();
    });

    it('devrait rejeter un profil avec des durées invalides', () => {
      const invalidBehaviorProfile = {
        browsingSpeed: 'normal',
        clickPattern: 'systematic',
        scrollBehavior: 'smooth',
        sessionDuration: { min: 30, max: 10 }, // min > max
        pageViewsPerSession: { min: 3, max: 10 },
        timeOnPage: { min: 10, max: 120 },
      };

      expect(() => BehaviorProfileSchema.parse(invalidBehaviorProfile)).toThrow();
    });
  });

  describe('DemographicsSchema', () => {
    it('devrait valider des données démographiques valides', () => {
      const validDemographics = {
        age: { min: 18, max: 65 },
        gender: 'male',
        location: { country: 'FR', region: 'Île-de-France', city: 'Paris' },
        interests: ['technology', 'gaming', 'sports'],
        occupation: 'Software Engineer',
      };

      expect(() => DemographicsSchema.parse(validDemographics)).not.toThrow();
    });

    it('devrait rejeter des données avec un âge invalide', () => {
      const invalidDemographics = {
        age: { min: 65, max: 18 }, // min > max
        gender: 'male',
        location: { country: 'FR' },
        interests: ['technology'],
      };

      expect(() => DemographicsSchema.parse(invalidDemographics)).toThrow();
    });

    it('devrait rejeter des données avec trop d\'intérêts', () => {
      const invalidDemographics = {
        age: { min: 18, max: 65 },
        gender: 'male',
        location: { country: 'FR' },
        interests: Array(25).fill('interest'), // trop d'intérêts
      };

      expect(() => DemographicsSchema.parse(invalidDemographics)).toThrow();
    });
  });

  describe('TechnicalProfileSchema', () => {
    it('devrait valider un profil technique valide', () => {
      const validTechnicalProfile = {
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

      expect(() => TechnicalProfileSchema.parse(validTechnicalProfile)).not.toThrow();
    });

    it('devrait rejeter un profil avec des probabilités qui ne somment pas à 1', () => {
      const invalidTechnicalProfile = {
        deviceTypes: [
          { type: 'desktop', probability: 0.7 },
          { type: 'mobile', probability: 0.5 }, // total = 1.2
        ],
        browsers: [
          { name: 'Chrome', version: '120', userAgent: 'Mozilla/5.0...', probability: 1.0 },
        ],
        operatingSystems: [
          { name: 'Windows', version: '10', probability: 1.0 },
        ],
        screenResolutions: [
          { width: 1920, height: 1080, probability: 1.0 },
        ],
        connectionTypes: [
          { type: 'wifi', speed: 'fast', probability: 1.0 },
        ],
        timezone: 'UTC',
      };

      expect(() => TechnicalProfileSchema.parse(invalidTechnicalProfile)).toThrow();
    });
  });

  describe('CampaignSchema', () => {
    it('devrait valider une campagne valide', () => {
      const validCampaign = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        name: 'Test Campaign',
        description: 'A test campaign for validation',
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

      expect(() => CampaignSchema.parse(validCampaign)).not.toThrow();
      expect(() => validateCampaign(validCampaign)).not.toThrow();
    });

    it('devrait rejeter une campagne avec une URL invalide', () => {
      const invalidCampaign = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        name: 'Test Campaign',
        description: 'A test campaign',
        targetUrl: 'not-a-valid-url',
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

      expect(() => CampaignSchema.parse(invalidCampaign)).toThrow();
    });
  });

  describe('SimulationConfigSchema', () => {
    it('devrait valider une configuration de simulation valide', () => {
      const validSimulationConfig = {
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

      expect(() => SimulationConfigSchema.parse(validSimulationConfig)).not.toThrow();
    });

    it('devrait rejeter une configuration avec des valeurs hors limites', () => {
      const invalidSimulationConfig = {
        concurrentSessions: 200, // trop élevé
        sessionInterval: 30,
        duration: 60,
        randomization: {
          enabled: true,
          timeVariation: 0.1,
          actionVariation: 0.1,
          pathVariation: 0.1,
        },
        behaviorVariation: 0.1,
      };

      expect(() => SimulationConfigSchema.parse(invalidSimulationConfig)).toThrow();
    });
  });

  describe('CreatePersonaRequestSchema', () => {
    it('devrait valider une requête de création de persona valide', () => {
      const validRequest = {
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
          browsers: [{ name: 'Chrome', version: '120', userAgent: 'Mozilla/5.0...', probability: 1.0 }],
          operatingSystems: [{ name: 'Windows', version: '10', probability: 1.0 }],
          screenResolutions: [{ width: 1920, height: 1080, probability: 1.0 }],
          connectionTypes: [{ type: 'wifi', speed: 'fast', probability: 1.0 }],
          timezone: 'UTC',
        },
      };

      expect(() => CreatePersonaRequestSchema.parse(validRequest)).not.toThrow();
      expect(() => validateCreatePersonaRequest(validRequest)).not.toThrow();
    });

    it('devrait rejeter une requête avec un nom vide', () => {
      const invalidRequest = {
        name: '',
        description: 'A new persona',
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
          browsers: [{ name: 'Chrome', version: '120', userAgent: 'Mozilla/5.0...', probability: 1.0 }],
          operatingSystems: [{ name: 'Windows', version: '10', probability: 1.0 }],
          screenResolutions: [{ width: 1920, height: 1080, probability: 1.0 }],
          connectionTypes: [{ type: 'wifi', speed: 'fast', probability: 1.0 }],
          timezone: 'UTC',
        },
      };

      expect(() => CreatePersonaRequestSchema.parse(invalidRequest)).toThrow();
    });
  });

  describe('CreateCampaignRequestSchema', () => {
    it('devrait valider une requête de création de campagne valide', () => {
      const validRequest = {
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

      expect(() => CreateCampaignRequestSchema.parse(validRequest)).not.toThrow();
      expect(() => validateCreateCampaignRequest(validRequest)).not.toThrow();
    });

    it('devrait rejeter une requête avec une URL invalide', () => {
      const invalidRequest = {
        name: 'New Campaign',
        description: 'A new campaign',
        targetUrl: 'not-a-valid-url',
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

      expect(() => CreateCampaignRequestSchema.parse(invalidRequest)).toThrow();
    });
  });

  describe('ApiResponseSchema', () => {
    it('devrait valider une réponse API valide', () => {
      const validResponse = {
        success: true,
        data: { id: '123', name: 'Test' },
        metadata: {
          timestamp: new Date(),
          requestId: '123e4567-e89b-12d3-a456-426614174000',
          version: 'v1',
        },
      };

      const schema = ApiResponseSchema({ id: 'string', name: 'string' });
      expect(() => schema.parse(validResponse)).not.toThrow();
    });

    it('devrait valider une réponse d\'erreur API', () => {
      const errorResponse = {
        success: false,
        error: {
          code: 'VALIDATION_ERROR',
          message: 'Invalid input data',
          timestamp: new Date(),
        },
      };

      const schema = ApiResponseSchema({ id: 'string', name: 'string' });
      expect(() => schema.parse(errorResponse)).not.toThrow();
    });
  });
});
