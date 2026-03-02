import { create } from "zustand";
import { ApiUser } from "../types";
import { authApi } from "../api/client";

interface AuthState {
  user: ApiUser | null;
  token: string | null;
  loading: boolean;
  setToken: (token: string) => void;
  logout: () => void;
  fetchMe: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem("token"),
  loading: false,

  setToken(token) {
    localStorage.setItem("token", token);
    set({ token });
  },

  logout() {
    localStorage.removeItem("token");
    set({ token: null, user: null });
  },

  async fetchMe() {
    set({ loading: true });
    try {
      const { data } = await authApi.me();
      set({ user: data });
    } catch {
      set({ user: null, token: null });
      localStorage.removeItem("token");
    } finally {
      set({ loading: false });
    }
  },
}));
