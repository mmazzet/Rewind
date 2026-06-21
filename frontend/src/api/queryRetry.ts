import type { AxiosError } from "axios";

export function shouldRetryQuery(
  failureCount: number,
  error: unknown,
): boolean {
  const status = (error as Partial<AxiosError>)?.response?.status;
  if (status !== undefined && status < 500) return false;
  return failureCount < 2;
}
