import apiClient from "@/api/client";
import type { User, LoginRequest, RegisterRequest } from "../types";

export const authApi = {
  register: async (data: RegisterRequest): Promise<User> => {
    const response = await apiClient.post<User>("/auth/register", data);
    return response.data;
  },

  login: async (data: LoginRequest): Promise<User> => {
    const response = await apiClient.post<User>("/auth/login", data);
    return response.data;
  },

  logout: async (): Promise<void> => {
    await apiClient.post("/auth/logout");
  },

  me: async (): Promise<User> => {
    const response = await apiClient.get<User>("/auth/me");
    return response.data;
  },

  verifyEmail: async (token: string): Promise<void> => {
    await apiClient.post("/auth/verify-email", { token });
  },
};
