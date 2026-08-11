import { useCallback } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { authApi } from "@/features/auth/api/authApi";
import useAuthStore from "@/store/authStore";

const navLinkClasses = ({ isActive }: { isActive: boolean }): string =>
  isActive
    ? "text-indigo-600 font-semibold"
    : "text-gray-600 hover:text-indigo-600 transition-colors";

function Nav(): React.ReactElement {
  const setUser = useAuthStore((state) => state.setUser);
  const user = useAuthStore((state) => state.user);
  const navigate = useNavigate();

  const handleLogout = useCallback(async () => {
    await authApi.logout();
    setUser(null);
    navigate("/login", { replace: true });
  }, [setUser, navigate]);

  return (
    <nav className="w-full bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
      <div className="flex items-center gap-6">
        <span className="font-bold text-gray-900 tracking-tight">Rewind</span>
        <NavLink to="/inbox" className={navLinkClasses}>
          Inbox
        </NavLink>
        <NavLink to="/outbox" className={navLinkClasses}>
          Outbox
        </NavLink>
        <NavLink to="/tapes/create" className={navLinkClasses}>
          New tape
        </NavLink>
      </div>
      <div className="flex items-center gap-4">
        <span className="text-sm text-gray-500">{user?.email}</span>
        <button
          onClick={handleLogout}
          className="text-sm text-gray-500 hover:text-red-500 transition-colors"
        >
          Log out
        </button>
      </div>
    </nav>
  );
}

export default Nav;
