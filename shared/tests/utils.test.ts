// Tests unitaires pour les utilitaires partagés
// Ces tests vérifient que les fonctions utilitaires fonctionnent correctement

import { describe, it, expect } from 'vitest';
import {
  // Type guards
  isPersona,
  isCampaign,
  isSession,
  
  // ID generation
  generateId,
  generateUUID,
  generateSessionId,
  
  // Date utilities
  formatDate,
  parseDate,
  addTime,
  getTimeDifference,
  isDateInRange,
  
  // Coordinate utilities
  calculateDistance,
  isPointInViewport,
  generateRandomCoordinates,
  
  // Pagination utilities
  calculatePagination,
  validatePagination,
  
  // String utilities
  truncateString,
  sanitizeString,
  generateSlug,
  
  // Array utilities
  chunkArray,
  shuffleArray,
  getRandomElement,
  getRandomElements,
  
  // Object utilities
  deepClone,
  pick,
  omit,
  
  // Math utilities
  clamp,
  lerp,
  randomBetween,
  randomInt,
  roundToDecimal,
  
  // Probability utilities
  weightedRandom,
  probability,
  
  // Analytics utilities
  calculateBounceRate,
  calculateAverageSessionDuration,
  calculateConversionRate,
  generateTrendData,
  calculateComparison,
  
  // Validation utilities
  isValidUrl,
  isValidEmail,
  isValidUUID,
  
  // Error utilities
  createError,
  isApiError,
  
  // Performance utilities
  debounce,
  throttle,
} from '../utils';

describe('Utilitaires Partagés', () => {
  describe('Type Guards', () => {
    it('devrait identifier correctement un persona valide', () => {
      const validPersona = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        name: 'Test Persona',
        description: 'A test persona',
        behaviorProfile: {},
        demographics: {},
        technicalProfile: {},
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      expect(isPersona(validPersona)).toBe(true);
    });

    it('devrait identifier correctement un objet non-persona', () => {
      const invalidPersona = {
        id: '123',
        name: 'Test',
      };

      expect(isPersona(invalidPersona)).toBe(false);
    });

    it('devrait identifier correctement une campagne valide', () => {
      const validCampaign = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        name: 'Test Campaign',
        targetUrl: 'https://example.com',
        personaIds: ['123e4567-e89b-12d3-a456-426614174001'],
        simulationConfig: {},
        status: 'draft',
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      expect(isCampaign(validCampaign)).toBe(true);
    });

    it('devrait identifier correctement une session valide', () => {
      const validSession = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        campaignId: '123e4567-e89b-12d3-a456-426614174001',
        personaId: '123e4567-e89b-12d3-a456-426614174002',
        sessionId: 'session_1234567890_abc123',
        status: 'pending',
        startTime: new Date(),
        userAgent: 'Mozilla/5.0...',
        ipAddress: '192.168.1.1',
        pageVisits: [],
        actions: [],
        metrics: {},
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      expect(isSession(validSession)).toBe(true);
    });
  });

  describe('Génération d\'IDs', () => {
    it('devrait générer un ID unique', () => {
      const id1 = generateId();
      const id2 = generateId();
      
      expect(id1).toBeDefined();
      expect(id2).toBeDefined();
      expect(id1).not.toBe(id2);
    });

    it('devrait générer un UUID valide', () => {
      const uuid = generateUUID();
      const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
      
      expect(uuid).toMatch(uuidRegex);
    });

    it('devrait générer un ID de session valide', () => {
      const sessionId = generateSessionId();
      
      expect(sessionId).toMatch(/^session_\d+_[a-z0-9]+$/);
    });
  });

  describe('Utilitaires de Date', () => {
    const testDate = new Date('2023-12-25T10:30:00Z');

    it('devrait formater une date en ISO', () => {
      const formatted = formatDate(testDate, 'iso');
      expect(formatted).toBe('2023-12-25T10:30:00.000Z');
    });

    it('devrait formater une date en format humain', () => {
      const formatted = formatDate(testDate, 'human');
      expect(formatted).toContain('2023');
    });

    it('devrait parser une date valide', () => {
      const parsed = parseDate('2023-12-25T10:30:00Z');
      expect(parsed).toBeInstanceOf(Date);
      expect(parsed.getTime()).toBe(testDate.getTime());
    });

    it('devrait rejeter une date invalide', () => {
      expect(() => parseDate('invalid-date')).toThrow();
    });

    it('devrait ajouter du temps à une date', () => {
      const newDate = addTime(testDate, 1, 'hours');
      expect(newDate.getHours()).toBe(11);
    });

    it('devrait calculer la différence de temps', () => {
      const start = new Date('2023-12-25T10:00:00Z');
      const end = new Date('2023-12-25T11:30:00Z');
      const diff = getTimeDifference(start, end, 'minutes');
      
      expect(diff).toBe(90);
    });

    it('devrait vérifier si une date est dans une plage', () => {
      const start = new Date('2023-12-25T10:00:00Z');
      const end = new Date('2023-12-25T12:00:00Z');
      const middle = new Date('2023-12-25T11:00:00Z');
      
      expect(isDateInRange(middle, start, end)).toBe(true);
      expect(isDateInRange(start, start, end)).toBe(true);
      expect(isDateInRange(end, start, end)).toBe(true);
    });
  });

  describe('Utilitaires de Coordonnées', () => {
    it('devrait calculer la distance entre deux points', () => {
      const point1 = { x: 0, y: 0 };
      const point2 = { x: 3, y: 4 };
      const distance = calculateDistance(point1, point2);
      
      expect(distance).toBe(5);
    });

    it('devrait vérifier si un point est dans le viewport', () => {
      const viewport = { width: 1920, height: 1080 };
      const pointIn = { x: 100, y: 100 };
      const pointOut = { x: 2000, y: 100 };
      
      expect(isPointInViewport(pointIn, viewport)).toBe(true);
      expect(isPointInViewport(pointOut, viewport)).toBe(false);
    });

    it('devrait générer des coordonnées aléatoires dans le viewport', () => {
      const viewport = { width: 1920, height: 1080 };
      const coords = generateRandomCoordinates(viewport);
      
      expect(coords.x).toBeGreaterThanOrEqual(0);
      expect(coords.x).toBeLessThanOrEqual(1920);
      expect(coords.y).toBeGreaterThanOrEqual(0);
      expect(coords.y).toBeLessThanOrEqual(1080);
    });
  });

  describe('Utilitaires de Pagination', () => {
    it('devrait calculer la pagination correctement', () => {
      const result = calculatePagination(2, 10, 25);
      
      expect(result.page).toBe(2);
      expect(result.limit).toBe(10);
      expect(result.total).toBe(25);
      expect(result.totalPages).toBe(3);
      expect(result.offset).toBe(10);
      expect(result.hasNext).toBe(true);
      expect(result.hasPrevious).toBe(true);
    });

    it('devrait valider les paramètres de pagination', () => {
      const valid = validatePagination(5, 50);
      expect(valid.page).toBe(5);
      expect(valid.limit).toBe(50);
    });

    it('devrait corriger les paramètres de pagination invalides', () => {
      const corrected = validatePagination(-1, 2000);
      expect(corrected.page).toBe(1);
      expect(corrected.limit).toBe(1000);
    });
  });

  describe('Utilitaires de Chaîne', () => {
    it('devrait tronquer une chaîne', () => {
      const longString = 'This is a very long string that should be truncated';
      const truncated = truncateString(longString, 20);
      
      expect(truncated).toBe('This is a very long...');
    });

    it('devrait nettoyer une chaîne', () => {
      const dirtyString = '<script>alert("xss")</script>';
      const clean = sanitizeString(dirtyString);
      
      expect(clean).toBe('&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;');
    });

    it('devrait générer un slug', () => {
      const title = 'Hello World! This is a Test';
      const slug = generateSlug(title);
      
      expect(slug).toBe('hello-world-this-is-a-test');
    });
  });

  describe('Utilitaires de Tableau', () => {
    it('devrait diviser un tableau en chunks', () => {
      const array = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
      const chunks = chunkArray(array, 3);
      
      expect(chunks).toHaveLength(4);
      expect(chunks[0]).toEqual([1, 2, 3]);
      expect(chunks[3]).toEqual([10]);
    });

    it('devrait mélanger un tableau', () => {
      const array = [1, 2, 3, 4, 5];
      const shuffled = shuffleArray(array);
      
      expect(shuffled).toHaveLength(5);
      expect(shuffled).toContain(1);
      expect(shuffled).toContain(2);
      expect(shuffled).toContain(3);
      expect(shuffled).toContain(4);
      expect(shuffled).toContain(5);
    });

    it('devrait obtenir un élément aléatoire', () => {
      const array = [1, 2, 3, 4, 5];
      const random = getRandomElement(array);
      
      expect(array).toContain(random);
    });

    it('devrait obtenir des éléments aléatoires', () => {
      const array = [1, 2, 3, 4, 5];
      const random = getRandomElements(array, 3);
      
      expect(random).toHaveLength(3);
      random.forEach(item => {
        expect(array).toContain(item);
      });
    });
  });

  describe('Utilitaires d\'Objet', () => {
    it('devrait cloner profondément un objet', () => {
      const original = {
        name: 'Test',
        nested: {
          value: 42,
          array: [1, 2, 3],
        },
      };
      const cloned = deepClone(original);
      
      expect(cloned).toEqual(original);
      expect(cloned).not.toBe(original);
      expect(cloned.nested).not.toBe(original.nested);
    });

    it('devrait extraire des propriétés spécifiques', () => {
      const obj = { a: 1, b: 2, c: 3 };
      const picked = pick(obj, ['a', 'c']);
      
      expect(picked).toEqual({ a: 1, c: 3 });
    });

    it('devrait omettre des propriétés spécifiques', () => {
      const obj = { a: 1, b: 2, c: 3 };
      const omitted = omit(obj, ['b']);
      
      expect(omitted).toEqual({ a: 1, c: 3 });
    });
  });

  describe('Utilitaires Mathématiques', () => {
    it('devrait contraindre une valeur dans une plage', () => {
      expect(clamp(5, 0, 10)).toBe(5);
      expect(clamp(-5, 0, 10)).toBe(0);
      expect(clamp(15, 0, 10)).toBe(10);
    });

    it('devrait interpoler linéairement', () => {
      expect(lerp(0, 10, 0.5)).toBe(5);
      expect(lerp(0, 10, 0)).toBe(0);
      expect(lerp(0, 10, 1)).toBe(10);
    });

    it('devrait générer un nombre aléatoire dans une plage', () => {
      const random = randomBetween(5, 10);
      expect(random).toBeGreaterThanOrEqual(5);
      expect(random).toBeLessThan(10);
    });

    it('devrait générer un entier aléatoire', () => {
      const random = randomInt(1, 6);
      expect(Number.isInteger(random)).toBe(true);
      expect(random).toBeGreaterThanOrEqual(1);
      expect(random).toBeLessThanOrEqual(6);
    });

    it('devrait arrondir à un nombre de décimales', () => {
      expect(roundToDecimal(3.14159, 2)).toBe(3.14);
      expect(roundToDecimal(3.14159, 0)).toBe(3);
    });
  });

  describe('Utilitaires de Probabilité', () => {
    it('devrait choisir un élément selon des poids', () => {
      const items = [
        { item: 'A', weight: 0.7 },
        { item: 'B', weight: 0.3 },
      ];
      
      // Test multiple times to ensure distribution
      const results = Array(100).fill(0).map(() => weightedRandom(items));
      const aCount = results.filter(r => r === 'A').length;
      const bCount = results.filter(r => r === 'B').length;
      
      expect(aCount + bCount).toBe(100);
      expect(aCount).toBeGreaterThan(bCount); // A should be more frequent
    });

    it('devrait retourner true/false selon une probabilité', () => {
      const results = Array(100).fill(0).map(() => probability(0.5));
      const trueCount = results.filter(r => r === true).length;
      
      expect(trueCount).toBeGreaterThan(20);
      expect(trueCount).toBeLessThan(80);
    });
  });

  describe('Utilitaires d\'Analytics', () => {
    const mockSessions = [
      {
        pageVisits: [{ url: 'page1' }],
        duration: 60,
        actions: [{ type: 'click' }],
      },
      {
        pageVisits: [{ url: 'page1' }, { url: 'page2' }],
        duration: 120,
        actions: [{ type: 'click' }, { type: 'scroll' }],
      },
      {
        pageVisits: [{ url: 'page1' }],
        duration: 30,
        actions: [{ type: 'click' }],
      },
    ] as any[];

    it('devrait calculer le taux de rebond', () => {
      const bounceRate = calculateBounceRate(mockSessions);
      expect(bounceRate).toBe(2/3); // 2 sessions with 1 page visit out of 3
    });

    it('devrait calculer la durée moyenne de session', () => {
      const avgDuration = calculateAverageSessionDuration(mockSessions);
      expect(avgDuration).toBe(70); // (60 + 120 + 30) / 3
    });

    it('devrait calculer le taux de conversion', () => {
      const conversionRate = calculateConversionRate(mockSessions, 'click');
      expect(conversionRate).toBe(1); // All sessions have click actions
    });

    it('devrait générer des données de tendance', () => {
      const data = [
        { timestamp: '2023-12-25T10:00:00Z', value: 10 },
        { timestamp: '2023-12-25T11:00:00Z', value: 20 },
        { timestamp: '2023-12-25T12:00:00Z', value: 15 },
      ];
      const trends = generateTrendData(data, 'timestamp', 'value', 'hour');
      
      expect(trends).toHaveLength(3);
      expect(trends[0].value).toBe(10);
    });

    it('devrait calculer une comparaison', () => {
      const comparison = calculateComparison(120, 100);
      
      expect(comparison.current).toBe(120);
      expect(comparison.previous).toBe(100);
      expect(comparison.change).toBe(20);
      expect(comparison.trend).toBe('up');
    });
  });

  describe('Utilitaires de Validation', () => {
    it('devrait valider une URL', () => {
      expect(isValidUrl('https://example.com')).toBe(true);
      expect(isValidUrl('http://localhost:3000')).toBe(true);
      expect(isValidUrl('not-a-url')).toBe(false);
    });

    it('devrait valider un email', () => {
      expect(isValidEmail('test@example.com')).toBe(true);
      expect(isValidEmail('user.name+tag@domain.co.uk')).toBe(true);
      expect(isValidEmail('invalid-email')).toBe(false);
    });

    it('devrait valider un UUID', () => {
      expect(isValidUUID('123e4567-e89b-12d3-a456-426614174000')).toBe(true);
      expect(isValidUUID('invalid-uuid')).toBe(false);
    });
  });

  describe('Utilitaires d\'Erreur', () => {
    it('devrait créer une erreur API', () => {
      const error = createError('VALIDATION_ERROR', 'Invalid input');
      
      expect(error.code).toBe('VALIDATION_ERROR');
      expect(error.message).toBe('Invalid input');
      expect(error.timestamp).toBeInstanceOf(Date);
    });

    it('devrait identifier une erreur API', () => {
      const apiError = createError('VALIDATION_ERROR', 'Invalid input');
      const regularError = new Error('Regular error');
      
      expect(isApiError(apiError)).toBe(true);
      expect(isApiError(regularError)).toBe(false);
    });
  });

  describe('Utilitaires de Performance', () => {
    it('devrait débouncer une fonction', (done) => {
      let callCount = 0;
      const debouncedFn = debounce(() => {
        callCount++;
        expect(callCount).toBe(1);
        done();
      }, 100);

      debouncedFn();
      debouncedFn();
      debouncedFn();
    });

    it('devrait throttler une fonction', (done) => {
      let callCount = 0;
      const throttledFn = throttle(() => {
        callCount++;
      }, 100);

      throttledFn();
      throttledFn();
      throttledFn();

      setTimeout(() => {
        expect(callCount).toBe(1);
        done();
      }, 150);
    });
  });
});
