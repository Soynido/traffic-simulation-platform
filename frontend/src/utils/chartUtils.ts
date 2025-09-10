// Chart utilities to normalize backend data for Recharts components

export type SessionItem = {
  created_at: string;
  status: string;
  completed_at?: string | null;
};

export type TimelinePoint = {
  timestamp: string; // ISO string
  sessions: number;
  completed: number;
  failed: number;
};

export const DEFAULT_COLORS = [
  '#3b82f6', // blue
  '#10b981', // emerald
  '#f59e0b', // amber
  '#ef4444', // red
  '#8b5cf6', // violet
  '#06b6d4', // cyan
  '#84cc16', // lime
  '#f97316', // orange
] as const;

// Buckets
export type TimeBucket = 'minute' | 'hour' | 'day';
const BUCKET_MS: Record<TimeBucket, number> = {
  minute: 60_000,
  hour: 3_600_000,
  day: 86_400_000,
};

function floorToBucket(dateMs: number, bucket: TimeBucket): number {
  const size = BUCKET_MS[bucket];
  return Math.floor(dateMs / size) * size;
}

export function buildSessionTimeline(
  sessions: SessionItem[],
  opts?: { bucket?: TimeBucket }
): TimelinePoint[] {
  const bucket = opts?.bucket ?? 'minute';
  const byBucket = new Map<number, { sessions: number; completed: number; failed: number }>();

  for (const s of sessions) {
    const t = new Date(s.created_at).getTime();
    const key = floorToBucket(t, bucket);
    const acc = byBucket.get(key) || { sessions: 0, completed: 0, failed: 0 };
    acc.sessions += 1;

    const st = String(s.status).toLowerCase();
    if (st.includes('complete')) acc.completed += 1;
    else if (st.includes('fail') || st.includes('error')) acc.failed += 1;

    byBucket.set(key, acc);
  }

  return [...byBucket.entries()]
    .sort((a, b) => a[0] - b[0])
    .map(([ms, v]) => ({ timestamp: new Date(ms).toISOString(), ...v }));
}

export function buildPersonaDistribution(
  sessions: Array<{ persona_id: string }>,
  personasById: Record<string, { name: string }>,
  colors: readonly string[] = DEFAULT_COLORS
): Array<{ name: string; value: number; color: string }> {
  const counts = new Map<string, number>();
  for (const s of sessions) {
    counts.set(s.persona_id, (counts.get(s.persona_id) || 0) + 1);
  }

  const entries = [...counts.entries()].map(([personaId, value], idx) => ({
    name: personasById[personaId]?.name || personaId,
    value,
    color: colors[idx % colors.length],
  }));

  // Sort desc by value for nicer legend ordering
  entries.sort((a, b) => b.value - a.value);
  return entries;
}

export type AnalyticsSummary = {
  success_rate?: number;
  avg_session_duration_ms?: number;
  avg_pages_per_session?: number;
  avg_actions_per_session?: number;
  avg_rhythm_score?: number;
  detection_risk_score?: number;
};

export function buildHumanVsSimulatedComparison(
  human: AnalyticsSummary,
  simulated: AnalyticsSummary
): Array<{ metric: string; human: number; simulated: number; difference: number }> {
  const metrics: Array<keyof AnalyticsSummary> = [
    'success_rate',
    'avg_session_duration_ms',
    'avg_pages_per_session',
    'avg_actions_per_session',
    'avg_rhythm_score',
    'detection_risk_score',
  ];

  const labelMap: Record<string, string> = {
    success_rate: 'Success Rate',
    avg_session_duration_ms: 'Avg Session Duration (ms)',
    avg_pages_per_session: 'Avg Pages/Session',
    avg_actions_per_session: 'Avg Actions/Session',
    avg_rhythm_score: 'Avg Rhythm Score',
    detection_risk_score: 'Detection Risk',
  };

  return metrics.map((m) => {
    const hv = Number(human[m] ?? 0);
    const sv = Number(simulated[m] ?? 0);
    return {
      metric: labelMap[m],
      human: hv,
      simulated: sv,
      difference: sv - hv,
    };
  });
}

// Formatting helpers
export const ms = (n: number | undefined | null) => (n ?? 0);
export const msToSeconds = (n: number | undefined | null) => ms(n) / 1000;
export function secondsToHHMMSS(totalSeconds: number): string {
  const s = Math.max(0, Math.floor(totalSeconds));
  const h = Math.floor(s / 3600).toString().padStart(2, '0');
  const m = Math.floor((s % 3600) / 60).toString().padStart(2, '0');
  const sec = (s % 60).toString().padStart(2, '0');
  return `${h}:${m}:${sec}`;
}

