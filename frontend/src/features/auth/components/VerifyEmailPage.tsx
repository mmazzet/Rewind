import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { authApi } from "../api/authApi";
import useAuthStore from "@/store/authStore";

type Status = "verifying" | "success" | "error";

function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const setUser = useAuthStore((state) => state.setUser);
  const [status, setStatus] = useState<Status>("verifying");

  useEffect(() => {
    const token = searchParams.get("token");

    if (!token) {
      setStatus("error");
      return;
    }

    authApi
      .verifyEmail(token)
      .then((user) => {
        setUser(user);
        setStatus("success");
        setTimeout(() => navigate("/inbox"), 2000);
      })
      .catch(() => {
        setStatus("error");
      });
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  if (status === "verifying") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="w-full max-w-md p-8 bg-white rounded-lg shadow">
          <p className="text-gray-600 text-sm">Verifying your email...</p>
        </div>
      </div>
    );
  }

  if (status === "success") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="w-full max-w-md p-8 bg-white rounded-lg shadow">
          <h1 className="text-2xl font-bold mb-4">Email verified</h1>
          <p className="text-gray-600 text-sm">Taking you to your inbox...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="w-full max-w-md p-8 bg-white rounded-lg shadow">
        <h1 className="text-2xl font-bold mb-4">Verification failed</h1>
        <p className="text-gray-600 text-sm mb-4">
          This link is invalid or has expired.
        </p>
        <a href="/register" className="text-blue-600 text-sm hover:underline">
          Back to register
        </a>
      </div>
    </div>
  );
}

export default VerifyEmailPage;
