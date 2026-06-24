import { useEffect, useState } from "react";
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
import AppErrorFallback from "@/components/AppErrorFallback"
import TapeBuilderErrorFallback from "@/components/TapeBuilderErrorFallback"

function HomePage() {
  const setUser = useAuthStore((state) => state.setUser);
  const user = useAuthStore((state) => state.user);

  const handleLogout = async () => {
    await authApi.logout();
    setUser(null);
  };

  return (
    <div className="p-8">
      <p className="mb-4">Logged in as: {user?.email}</p>
      <button
        onClick={handleLogout}
        className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
      >
        Log out
      </button>
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
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <HomePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/tapes/create"
            element={
              <ProtectedRoute>
                <CreateTapePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/tapes/:tapeId"
            element={
              <ProtectedRoute>
                <ErrorBoundary fallback={(error) => <TapeBuilderErrorFallback error={error} />}>
                <TapeBuilderPage />
                </ErrorBoundary>
              </ProtectedRoute>
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
