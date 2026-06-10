import axios from "axios";

const apiClient = axios.create({
  baseURL: "/api/v1",
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

function getCsrfToken(): string | null {
  const match = document.cookie
    .split("; ")
    .find((row) => row.startsWith("csrf_token="));
  return match ? match.split("=")[1] : null;
}

apiClient.interceptors.request.use((config) => {
  const token = getCsrfToken();
  if (token) {
    config.headers["X-CSRF-Token"] = token;
  }
  return config;
});

export default apiClient;
