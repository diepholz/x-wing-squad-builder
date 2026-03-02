import axios from "axios";

const api = axios.create({ baseURL: "/api" });

// Attach JWT from localStorage to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;

// ── Auth ──────────────────────────────────────────────────────────────────────

export const authApi = {
  register: (data: { username: string; email: string; password: string }) =>
    api.post<{ access_token: string }>("/auth/register", data),

  login: (username: string, password: string) => {
    const form = new URLSearchParams();
    form.append("username", username);
    form.append("password", password);
    return api.post<{ access_token: string }>("/auth/login", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
  },

  me: () => api.get("/auth/me"),
};

// ── Definition data ───────────────────────────────────────────────────────────

export const dataApi = {
  definition: () => api.get("/data/definition"),
};

// ── Squads ────────────────────────────────────────────────────────────────────

export const squadsApi = {
  list: () => api.get("/squads"),
  create: (payload: { name: string; faction: string; data: unknown }) =>
    api.post("/squads", payload),
  get: (id: number) => api.get(`/squads/${id}`),
  update: (id: number, payload: Partial<{ name: string; faction: string; data: unknown }>) =>
    api.put(`/squads/${id}`, payload),
  delete: (id: number) => api.delete(`/squads/${id}`),
  share: (id: number) => api.post(`/squads/${id}/share`),
  viewShared: (token: string) => api.get(`/squads/share/${token}`),
};
