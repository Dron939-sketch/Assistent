import axios from "axios";
import { getSession } from "next-auth/react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(async (config) => {
  const session = await getSession();
  if (session?.accessToken) {
    config.headers.Authorization = `Bearer ${session.accessToken}`;
  }
  return config;
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
      if (typeof window !== "undefined") {
        window.location.href = "/auth/login";
      }
    }
    return Promise.reject(error);
  }
);

// API functions
export const api = {
  // Auth
  auth: {
    login: (email: string, password: string) =>
      apiClient.post("/auth/login", { email, password }),
    register: (data: any) => apiClient.post("/auth/register", data),
    getMe: () => apiClient.get("/auth/me"),
  },

  // Audit
  audit: {
    createVK: (vk_page_url: string) =>
      apiClient.post("/audit/vk", { vk_page_url }),
    get: (auditId: string) => apiClient.get(`/audit/vk/${auditId}`),
    list: () => apiClient.get("/audit/vk"),
  },

  // Content
  content: {
    generatePost: (data: any) => apiClient.post("/content/generate/post", data),
    generateCase: (data: any) => apiClient.post("/content/generate/case", data),
    generateReply: (message: string) =>
      apiClient.post("/content/generate/reply", { message }),
    schedule: (data: any) => apiClient.post("/content/schedule", data),
    getCalendar: () => apiClient.get("/content/calendar"),
  },

  // Funnel
  funnel: {
    create: (data: any) => apiClient.post("/funnel/funnels", data),
    list: () => apiClient.get("/funnel/funnels"),
    get: (id: string) => apiClient.get(`/funnel/funnels/${id}`),
    update: (id: string, data: any) =>
      apiClient.put(`/funnel/funnels/${id}`, data),
    delete: (id: string) => apiClient.delete(`/funnel/funnels/${id}`),
    getLeads: () => apiClient.get("/funnel/leads"),
    updateLeadStatus: (id: string, status: string) =>
      apiClient.post(`/funnel/leads/${id}/status`, { status }),
  },

  // Marathon
  marathon: {
    generate: (data: any) => apiClient.post("/marathon/generate", data),
    create: (data: any) => apiClient.post("/marathon", data),
    list: () => apiClient.get("/marathon"),
    get: (id: string) => apiClient.get(`/marathon/${id}`),
    update: (id: string, data: any) => apiClient.put(`/marathon/${id}`, data),
    delete: (id: string) => apiClient.delete(`/marathon/${id}`),
    publish: (id: string) => apiClient.post(`/marathon/${id}/publish`),
    register: (id: string, data: any) =>
      apiClient.post(`/marathon/${id}/register`, data),
    getParticipants: (id: string) => apiClient.get(`/marathon/${id}/participants`),
    submitHomework: (data: any) => apiClient.post("/marathon/homework/submit", data),
    getStats: (id: string) => apiClient.get(`/marathon/${id}/stats`),
  },

  // Analytics
  analytics: {
    getDashboard: () => apiClient.get("/analytics/dashboard"),
    getLeadsChart: () => apiClient.get("/analytics/leads-chart"),
    getEngagementChart: () => apiClient.get("/analytics/engagement-chart"),
    getLeveragePoints: () => apiClient.get("/analytics/leverage"),
    completeLeveragePoint: (id: string, data: any) =>
      apiClient.post(`/analytics/leverage/${id}/complete`, data),
    getForecast: () => apiClient.get("/analytics/forecast"),
    getROI: () => apiClient.get("/analytics/roi"),
  },

  // Brand
  brand: {
    generatePositioning: (data: any) =>
      apiClient.post("/brand/positioning", data),
    generateStory: (data: any) => apiClient.post("/brand/story", data),
    trustAudit: (data: any) => apiClient.post("/brand/trust-audit", data),
    analyzeUniqueness: (data: any) => apiClient.post("/brand/uniqueness", data),
    generateLandingPage: (data: any) =>
      apiClient.post("/brand/landing-page", data),
  },
};
