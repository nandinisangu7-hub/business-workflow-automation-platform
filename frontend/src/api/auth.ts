import api from "./client";
import type { TokenResponse, User } from "../types";

export const authApi = {
  register: (email: string, full_name: string, password: string) =>
    api.post<User>("/auth/register", { email, full_name, password }),

  login: (email: string, password: string) => {
    const form = new URLSearchParams();
    form.append("username", email);
    form.append("password", password);
    return api.post<TokenResponse>("/auth/login", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
  },

  me: () => api.get<User>("/auth/me"),
};
