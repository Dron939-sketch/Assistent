import axios, { AxiosError, AxiosResponse, InternalAxiosRequestConfig } from "axios";
import { getSession } from "next-auth/react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const DEBUG = process.env.NEXT_PUBLIC_DEBUG === "true" || process.env.NODE_ENV !== "production";

export const apiClient = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
});

apiClient.interceptors.request.use(async (config: InternalAxiosRequestConfig) => {
  const session = await getSession();
  if (session?.accessToken) {
    config.headers.Authorization = `Bearer ${session.accessToken}`;
  }
  if (DEBUG) {
    // eslint-disable-next-line no-console
    console.debug(
      `[api] -> ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`,
    );
  }
  return config;
});

apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    if (DEBUG) {
      // eslint-disable-next-line no-console
      console.debug(
        `[api] <- ${response.status} ${response.config.method?.toUpperCase()} ${response.config.url}`,
      );
    }
    return response;
  },
  async (error: AxiosError) => {
    const status = error.response?.status;
    const method = error.config?.method?.toUpperCase();
    const url = `${error.config?.baseURL ?? ""}${error.config?.url ?? ""}`;
    const body = error.response?.data;

    // eslint-disable-next-line no-console
    console.error(
      `[api] ✗ ${status ?? "network"} ${method} ${url} message="${error.message}"`,
      body,
    );

    if (status === 401 && typeof window !== "undefined") {
      window.location.href = "/auth/login";
    }
    return Promise.reject(error);
  },
);

type AnyData = Record<string, unknown>;

export const api = {
  auth: {
    login: (email: string, password: string) =>
      apiClient.post("/auth/login", { email, password }),
    register: (data: AnyData) => apiClient.post("/auth/register", data),
    getMe: () => apiClient.get("/auth/me"),
  },

  audit: {
    createVK: (vk_page_url: string) =>
      apiClient.post("/audit/vk", { vk_page_url }),
    get: (auditId: string) => apiClient.get(`/audit/vk/${auditId}`),
    list: () => apiClient.get("/audit/vk"),
  },

  content: {
    generatePost: (data: AnyData) => apiClient.post("/content/generate/post", data),
    generateCase: (data: AnyData) => apiClient.post("/content/generate/case", data),
    generateReply: (message: string) =>
      apiClient.post("/content/generate/reply", { message }),
    schedule: (data: AnyData) => apiClient.post("/content/schedule", data),
    getCalendar: () => apiClient.get("/content/calendar"),
  },

  funnel: {
    create: (data: AnyData) => apiClient.post("/funnel/funnels", data),
    list: () => apiClient.get("/funnel/funnels"),
    get: (id: string) => apiClient.get(`/funnel/funnels/${id}`),
    update: (id: string, data: AnyData) =>
      apiClient.put(`/funnel/funnels/${id}`, data),
    delete: (id: string) => apiClient.delete(`/funnel/funnels/${id}`),
    getLeads: () => apiClient.get("/funnel/leads"),
    updateLeadStatus: (id: string, status: string) =>
      apiClient.post(`/funnel/leads/${id}/status`, { status }),
  },

  marathon: {
    generate: (data: AnyData) => apiClient.post("/marathon/generate", data),
    create: (data: AnyData) => apiClient.post("/marathon", data),
    list: () => apiClient.get("/marathon"),
    get: (id: string) => apiClient.get(`/marathon/${id}`),
    update: (id: string, data: AnyData) => apiClient.put(`/marathon/${id}`, data),
    delete: (id: string) => apiClient.delete(`/marathon/${id}`),
    publish: (id: string) => apiClient.post(`/marathon/${id}/publish`),
    register: (id: string, data: AnyData) =>
      apiClient.post(`/marathon/${id}/register`, data),
    getParticipants: (id: string) => apiClient.get(`/marathon/${id}/participants`),
    submitHomework: (data: AnyData) => apiClient.post("/marathon/homework/submit", data),
    getStats: (id: string) => apiClient.get(`/marathon/${id}/stats`),
  },

  analytics: {
    getDashboard: () => apiClient.get("/analytics/dashboard"),
    getLeadsChart: () => apiClient.get("/analytics/leads-chart"),
    getEngagementChart: () => apiClient.get("/analytics/engagement-chart"),
    getLeveragePoints: () => apiClient.get("/analytics/leverage"),
    completeLeveragePoint: (id: string, data: AnyData) =>
      apiClient.post(`/analytics/leverage/${id}/complete`, data),
    getForecast: () => apiClient.get("/analytics/forecast"),
    getROI: () => apiClient.get("/analytics/roi"),
  },

  brand: {
    generatePositioning: (data: AnyData) =>
      apiClient.post("/brand/positioning", data),
    generateStory: (data: AnyData) => apiClient.post("/brand/story", data),
    trustAudit: (data: AnyData) => apiClient.post("/brand/trust-audit", data),
    analyzeUniqueness: (data: AnyData) => apiClient.post("/brand/uniqueness", data),
    generateLandingPage: (data: AnyData) =>
      apiClient.post("/brand/landing-page", data),
  },
};
