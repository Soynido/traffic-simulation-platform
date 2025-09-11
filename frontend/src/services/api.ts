import axios, { AxiosInstance, AxiosRequestConfig, AxiosError } from 'axios';

// Direct connection to backend - simpler and more reliable
const BASE_URL = typeof window !== 'undefined' 
  ? 'http://localhost:8000/api/v1'  // Browser: direct backend call
  : process.env.API_URL || 'http://backend:8000/api/v1';  // Server: direct backend call

function createClient(): AxiosInstance {
  const instance = axios.create({
    baseURL: BASE_URL,
    timeout: 30000,  // Increased timeout for Docker network
    headers: {
      'Content-Type': 'application/json',
    },
  });

  instance.interceptors.response.use(
    (res) => res,
    (error: AxiosError) => {
      // Normalize error shape
      const status = error.response?.status;
      const message = (error.response?.data as any)?.detail || error.message;
      return Promise.reject({ status, message, error });
    }
  );

  return instance;
}

export const api: AxiosInstance = createClient();

// Example typed helpers (extend as needed)
export type Persona = {
  id: string;
  name: string;
  description?: string | null;
  session_duration_min: number;
  session_duration_max: number;
  pages_min: number;
  pages_max: number;
  actions_per_page_min: number;
  actions_per_page_max: number;
  scroll_probability: number;
  click_probability: number;
  typing_probability: number;
  created_at: string;
  updated_at: string;
};

export type PersonaCreate = Omit<Persona,
  'id' | 'created_at' | 'updated_at'
>;

export type PersonaUpdate = Partial<PersonaCreate>;

export async function listPersonas(params?: { page?: number; limit?: number; name?: string }) {
  const res = await api.get('/personas', { params });
  return res.data;
}

export async function createPersona(payload: PersonaCreate): Promise<Persona> {
  const res = await api.post('/personas', payload);
  return res.data;
}

export async function updatePersona(id: string, payload: PersonaUpdate): Promise<Persona> {
  const res = await api.put(`/personas/${id}`, payload);
  return res.data;
}

export async function deletePersona(id: string): Promise<void> {
  await api.delete(`/personas/${id}`);
}

