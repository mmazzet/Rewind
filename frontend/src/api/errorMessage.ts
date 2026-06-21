import { AxiosError } from "axios";

export function getErrorMessage(error: unknown, fallback: string): string {
  if (error instanceof AxiosError) {
    const data = error.response?.data as
      | { detail?: string; message?: string }
      | undefined;
    return data?.detail ?? data?.message ?? fallback;
  }
  return fallback;
}
