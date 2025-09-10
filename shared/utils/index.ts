// Utilitaires partagés entre frontend et backend
// Ces fonctions peuvent être utilisées côté client et serveur

import type { 
  Persona, 
  Campaign, 
  Session, 
  PageVisit, 
  Action, 
  Coordinates,
  ViewportSize,
  TimePeriod,
  TrendData,
  ComparisonData,
  Insight,
} from '../types';
import { 
  HTTP_STATUS, 
  ERROR_CODES, 
  TIME, 
  PAGINATION,
  ANALYTICS,
} from '../constants';

// ===== TYPE GUARDS =====

export const isPersona = (obj: any): obj is Persona => {
  return obj && 
    typeof obj.id === 'string' &&
    typeof obj.name === 'string' &&
    typeof obj.description === 'string' &&
    typeof obj.isActive === 'boolean' &&
    obj.behaviorProfile &&
    obj.demographics &&
    obj.technicalProfile;
};

export const isCampaign = (obj: any): obj is Campaign => {
  return obj &&
    typeof obj.id === 'string' &&
    typeof obj.name === 'string' &&
    typeof obj.targetUrl === 'string' &&
    Array.isArray(obj.personaIds) &&
    obj.simulationConfig &&
    typeof obj.status === 'string';
};

export const isSession = (obj: any): obj is Session => {
  return obj &&
    typeof obj.id === 'string' &&
    typeof obj.campaignId === 'string' &&
    typeof obj.personaId === 'string' &&
    typeof obj.sessionId === 'string' &&
    typeof obj.status === 'string' &&
    obj.startTime instanceof Date;
};

// ===== ID GENERATION =====

export const generateId = (): string => {
  return Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
};

export const generateUUID = (): string => {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
};

export const generateSessionId = (): string => {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

// ===== DATE UTILITIES =====

export const formatDate = (date: Date, format: 'iso' | 'human' | 'timestamp' = 'iso'): string => {
  switch (format) {
    case 'iso':
      return date.toISOString();
    case 'human':
      return date.toLocaleString();
    case 'timestamp':
      return date.getTime().toString();
    default:
      return date.toISOString();
  }
};

export const parseDate = (dateString: string): Date => {
  const date = new Date(dateString);
  if (isNaN(date.getTime())) {
    throw new Error(`Invalid date string: ${dateString}`);
  }
  return date;
};

export const addTime = (date: Date, amount: number, unit: 'seconds' | 'minutes' | 'hours' | 'days'): Date => {
  const newDate = new Date(date);
  switch (unit) {
    case 'seconds':
      newDate.setSeconds(newDate.getSeconds() + amount);
      break;
    case 'minutes':
      newDate.setMinutes(newDate.getMinutes() + amount);
      break;
    case 'hours':
      newDate.setHours(newDate.getHours() + amount);
      break;
    case 'days':
      newDate.setDate(newDate.getDate() + amount);
      break;
  }
  return newDate;
};

export const getTimeDifference = (start: Date, end: Date, unit: 'seconds' | 'minutes' | 'hours' | 'days' = 'seconds'): number => {
  const diff = end.getTime() - start.getTime();
  switch (unit) {
    case 'seconds':
      return Math.floor(diff / TIME.SECOND);
    case 'minutes':
      return Math.floor(diff / TIME.MINUTE);
    case 'hours':
      return Math.floor(diff / TIME.HOUR);
    case 'days':
      return Math.floor(diff / TIME.DAY);
    default:
      return diff;
  }
};

export const isDateInRange = (date: Date, start: Date, end: Date): boolean => {
  return date >= start && date <= end;
};

// ===== COORDINATE UTILITIES =====

export const calculateDistance = (point1: Coordinates, point2: Coordinates): number => {
  const dx = point2.x - point1.x;
  const dy = point2.y - point1.y;
  return Math.sqrt(dx * dx + dy * dy);
};

export const isPointInViewport = (point: Coordinates, viewport: ViewportSize): boolean => {
  return point.x >= 0 && point.x <= viewport.width && 
         point.y >= 0 && point.y <= viewport.height;
};

export const generateRandomCoordinates = (viewport: ViewportSize): Coordinates => {
  return {
    x: Math.random() * viewport.width,
    y: Math.random() * viewport.height,
  };
};

// ===== PAGINATION UTILITIES =====

export const calculatePagination = (
  page: number = PAGINATION.DEFAULT_PAGE,
  limit: number = PAGINATION.DEFAULT_LIMIT,
  total: number
) => {
  const totalPages = Math.ceil(total / limit);
  const offset = (page - 1) * limit;
  
  return {
    page,
    limit,
    total,
    totalPages,
    offset,
    hasNext: page < totalPages,
    hasPrevious: page > 1,
  };
};

export const validatePagination = (page?: number, limit?: number): { page: number; limit: number } => {
  const validPage = Math.max(1, page || PAGINATION.DEFAULT_PAGE);
  const validLimit = Math.min(
    Math.max(1, limit || PAGINATION.DEFAULT_LIMIT),
    PAGINATION.MAX_LIMIT
  );
  
  return { page: validPage, limit: validLimit };
};

// ===== STRING UTILITIES =====

export const truncateString = (str: string, maxLength: number, suffix: string = '...'): string => {
  if (str.length <= maxLength) return str;
  return str.substring(0, maxLength - suffix.length) + suffix;
};

export const sanitizeString = (str: string): string => {
  return str.replace(/[<>\"'&]/g, (match) => {
    switch (match) {
      case '<': return '&lt;';
      case '>': return '&gt;';
      case '"': return '&quot;';
      case "'": return '&#x27;';
      case '&': return '&amp;';
      default: return match;
    }
  });
};

export const generateSlug = (str: string): string => {
  return str
    .toLowerCase()
    .replace(/[^a-z0-9 -]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .trim();
};

// ===== ARRAY UTILITIES =====

export const chunkArray = <T>(array: T[], size: number): T[][] => {
  const chunks: T[][] = [];
  for (let i = 0; i < array.length; i += size) {
    chunks.push(array.slice(i, i + size));
  }
  return chunks;
};

export const shuffleArray = <T>(array: T[]): T[] => {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
};

export const getRandomElement = <T>(array: T[]): T | undefined => {
  if (array.length === 0) return undefined;
  return array[Math.floor(Math.random() * array.length)];
};

export const getRandomElements = <T>(array: T[], count: number): T[] => {
  const shuffled = shuffleArray(array);
  return shuffled.slice(0, Math.min(count, array.length));
};

// ===== OBJECT UTILITIES =====

export const deepClone = <T>(obj: T): T => {
  if (obj === null || typeof obj !== 'object') return obj;
  if (obj instanceof Date) return new Date(obj.getTime()) as any;
  if (obj instanceof Array) return obj.map(item => deepClone(item)) as any;
  if (typeof obj === 'object') {
    const cloned: any = {};
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        cloned[key] = deepClone(obj[key]);
      }
    }
    return cloned;
  }
  return obj;
};

export const pick = <T, K extends keyof T>(obj: T, keys: K[]): Pick<T, K> => {
  const result = {} as Pick<T, K>;
  keys.forEach(key => {
    if (key in obj) {
      result[key] = obj[key];
    }
  });
  return result;
};

export const omit = <T, K extends keyof T>(obj: T, keys: K[]): Omit<T, K> => {
  const result = { ...obj };
  keys.forEach(key => {
    delete result[key];
  });
  return result;
};

// ===== MATH UTILITIES =====

export const clamp = (value: number, min: number, max: number): number => {
  return Math.min(Math.max(value, min), max);
};

export const lerp = (start: number, end: number, factor: number): number => {
  return start + (end - start) * factor;
};

export const randomBetween = (min: number, max: number): number => {
  return Math.random() * (max - min) + min;
};

export const randomInt = (min: number, max: number): number => {
  return Math.floor(Math.random() * (max - min + 1)) + min;
};

export const roundToDecimal = (value: number, decimals: number): number => {
  return Math.round(value * Math.pow(10, decimals)) / Math.pow(10, decimals);
};

// ===== PROBABILITY UTILITIES =====

export const weightedRandom = <T>(items: Array<{ item: T; weight: number }>): T => {
  const totalWeight = items.reduce((sum, { weight }) => sum + weight, 0);
  let random = Math.random() * totalWeight;
  
  for (const { item, weight } of items) {
    random -= weight;
    if (random <= 0) return item;
  }
  
  return items[items.length - 1].item;
};

export const probability = (chance: number): boolean => {
  return Math.random() < chance;
};

// ===== ANALYTICS UTILITIES =====

export const calculateBounceRate = (sessions: Session[]): number => {
  if (sessions.length === 0) return 0;
  const bouncedSessions = sessions.filter(session => session.pageVisits.length <= 1);
  return bouncedSessions.length / sessions.length;
};

export const calculateAverageSessionDuration = (sessions: Session[]): number => {
  if (sessions.length === 0) return 0;
  const totalDuration = sessions.reduce((sum, session) => {
    return sum + (session.duration || 0);
  }, 0);
  return totalDuration / sessions.length;
};

export const calculateConversionRate = (sessions: Session[], conversionAction: string): number => {
  if (sessions.length === 0) return 0;
  const convertedSessions = sessions.filter(session => 
    session.actions.some(action => action.type === conversionAction)
  );
  return convertedSessions.length / sessions.length;
};

export const generateTrendData = (
  data: any[],
  timeField: string,
  valueField: string,
  granularity: TimePeriod['granularity']
): TrendData[] => {
  // Group data by time granularity
  const grouped = data.reduce((acc, item) => {
    const date = new Date(item[timeField]);
    let key: string;
    
    switch (granularity) {
      case 'minute':
        key = `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}-${date.getHours()}-${date.getMinutes()}`;
        break;
      case 'hour':
        key = `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}-${date.getHours()}`;
        break;
      case 'day':
        key = `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;
        break;
      case 'week':
        const week = Math.ceil(date.getDate() / 7);
        key = `${date.getFullYear()}-${date.getMonth()}-W${week}`;
        break;
      case 'month':
        key = `${date.getFullYear()}-${date.getMonth()}`;
        break;
      default:
        key = date.toISOString();
    }
    
    if (!acc[key]) acc[key] = [];
    acc[key].push(item);
    return acc;
  }, {} as Record<string, any[]>);
  
  // Calculate aggregated values
  return Object.entries(grouped).map(([key, items]) => ({
    timestamp: new Date(key),
    value: items.reduce((sum, item) => sum + (item[valueField] || 0), 0),
    metric: valueField,
  }));
};

export const calculateComparison = (
  current: number,
  previous: number
): ComparisonData => {
  const change = previous === 0 ? 0 : ((current - previous) / previous) * 100;
  const trend = change > 5 ? 'up' : change < -5 ? 'down' : 'stable';
  
  return {
    metric: 'value',
    current,
    previous,
    change: roundToDecimal(change, 2),
    trend,
  };
};

// ===== VALIDATION UTILITIES =====

export const isValidUrl = (url: string): boolean => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const isValidUUID = (uuid: string): boolean => {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  return uuidRegex.test(uuid);
};

// ===== ERROR UTILITIES =====

export const createError = (code: string, message: string, details?: any) => {
  return {
    code,
    message,
    details,
    timestamp: new Date(),
  };
};

export const isApiError = (error: any): boolean => {
  return error && 
    typeof error.code === 'string' && 
    typeof error.message === 'string' &&
    error.timestamp instanceof Date;
};

// ===== PERFORMANCE UTILITIES =====

export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle: boolean;
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};

export const measurePerformance = async <T>(
  name: string,
  fn: () => Promise<T>
): Promise<T> => {
  const start = performance.now();
  try {
    const result = await fn();
    const end = performance.now();
    console.log(`${name} took ${end - start} milliseconds`);
    return result;
  } catch (error) {
    const end = performance.now();
    console.error(`${name} failed after ${end - start} milliseconds:`, error);
    throw error;
  }
};

// ===== EXPORT ALL UTILITIES =====

export {
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
  measurePerformance,
};
