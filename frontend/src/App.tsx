import { Suspense, useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "@/features/auth/components/LoginPage";
import RegisterPage from "@/features/auth/components/RegisterPage";
import ProtectedRoute from "@/components/ProtectedRoute";
import { authApi } from "@/features/auth/api/authApi";
import useAuthStore from "@/store/authStore";
import { CreateTapePage } from "@/features/tapes/components/CreateTapePage";
import { TapeBuilderPage } from "@/features/tapes/components/TapeBuilderPage";
import { Toaster } from "react-hot-toast";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import AppErrorFallback from "@/components/AppErrorFallback";
import TapeBuilderErrorFallback from "@/components/TapeBuilderErrorFallback";
import PublicTapePage from "@/features/tapes/components/PublicTapePage";
import OutboxPage from "@/features/outbox/components/OutboxPage";
import InboxPage from "@/features/inbox/components/InboxPage";
import Nav from "@/components/Nav";
import VerifyEmailPage from "@/features/auth/components/VerifyEmailPage";
import SpotifyCallbackPage from "@/features/tapes/components/SpotifyCallbackPage";

function ProtectedLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-50">
      <Nav />
      <main>{children}</main>
    </div>
  );
}

function App() {
  const setUser = useAuthStore((state) => state.setUser);
  const [authChecked, setAuthChecked] = useState(false);

  useEffect(() => {
    authApi
      .me()
      .then((user) => {
        setUser(user);
      })
      .catch(() => {
        setUser(null);
      })
      .finally(() => {
        setAuthChecked(true);
      });
  }, [setUser]);

  if (!authChecked) return null;

  return (
    <>
      <Toaster />
      <BrowserRouter>
        <ErrorBoundary fallback={() => <AppErrorFallback />}>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/verify-email" element={<VerifyEmailPage />} />
            <Route path="/spotify/callback" element={<SpotifyCallbackPage />} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Navigate to="/inbox" replace />
                </ProtectedRoute>
              }
            />
            <Route
              path="/tapes/create"
              element={
                <ProtectedRoute>
                  <ProtectedLayout>
                    <CreateTapePage />
                  </ProtectedLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/tapes/:tapeId"
              element={
                <ProtectedRoute>
                  <ProtectedLayout>
                    <ErrorBoundary
                      fallback={(error) => (
                        <TapeBuilderErrorFallback error={error} />
                      )}
                    >
                      <TapeBuilderPage />
                    </ErrorBoundary>
                  </ProtectedLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/outbox"
              element={
                <ProtectedRoute>
                  <ProtectedLayout>
                    <Suspense fallback={null}>
                      <OutboxPage />
                    </Suspense>
                  </ProtectedLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/inbox"
              element={
                <ProtectedRoute>
                  <ProtectedLayout>
                    <Suspense fallback={null}>
                      <InboxPage />
                    </Suspense>
                  </ProtectedLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/tape/:token"
              element={
                <ErrorBoundary fallback={() => <AppErrorFallback />}>
                  <Suspense fallback={null}>
                    <PublicTapePage />
                  </Suspense>
                </ErrorBoundary>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </ErrorBoundary>
      </BrowserRouter>
    </>
  );
}

export default App;
