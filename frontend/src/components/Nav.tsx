import { useCallback, useEffect, useRef, useState } from "react";
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
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const menuRef = useRef<HTMLElement>(null);

  const closeMenu = useCallback(() => setIsMenuOpen(false), []);

  useEffect(() => {
    if (!isMenuOpen) return;

    const handlePointerDown = (event: PointerEvent) => {
      if (
        menuRef.current &&
        !menuRef.current.contains(event.target as Node)
      ) {
        setIsMenuOpen(false);
      }
    };
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setIsMenuOpen(false);
      }
    };

    document.addEventListener("pointerdown", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("pointerdown", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isMenuOpen]);

  const handleLogout = useCallback(async () => {
    await authApi.logout();
    setUser(null);
    navigate("/login", { replace: true });
  }, [setUser, navigate]);

  return (
    <nav
      ref={menuRef}
      className="w-full bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between relative"
    >
      <div className="flex items-center gap-6">
        <span className="font-bold text-gray-900 tracking-tight">Rewind</span>
        <div className="hidden md:flex items-center gap-6">
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
      </div>

      <div className="hidden md:flex items-center gap-4">
        <span className="text-sm text-gray-500">{user?.email}</span>
        <button
          onClick={handleLogout}
          className="text-sm text-gray-500 hover:text-red-500 transition-colors"
        >
          Log out
        </button>
      </div>

      <button
        type="button"
        onClick={() => setIsMenuOpen((open) => !open)}
        aria-label={isMenuOpen ? "Close menu" : "Open menu"}
        aria-expanded={isMenuOpen}
        className="md:hidden p-2 -mr-2 text-gray-700 hover:text-indigo-600 transition-colors"
      >
        {isMenuOpen ? (
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            aria-hidden="true"
          >
            <path d="M18 6 6 18" />
            <path d="m6 6 12 12" />
          </svg>
        ) : (
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            aria-hidden="true"
          >
            <path d="M4 6h16" />
            <path d="M4 12h16" />
            <path d="M4 18h16" />
          </svg>
        )}
      </button>

      {isMenuOpen && (
        <div className="absolute top-full left-0 right-0 bg-white border-b border-gray-200 shadow-md md:hidden flex flex-col px-6 py-2">
          <NavLink
            to="/inbox"
            onClick={closeMenu}
            className={({ isActive }) =>
              `py-3 text-base ${
                isActive
                  ? "text-indigo-600 font-semibold"
                  : "text-gray-600 hover:text-indigo-600 transition-colors"
              }`
            }
          >
            Inbox
          </NavLink>
          <NavLink
            to="/outbox"
            onClick={closeMenu}
            className={({ isActive }) =>
              `py-3 text-base border-t border-gray-100 ${
                isActive
                  ? "text-indigo-600 font-semibold"
                  : "text-gray-600 hover:text-indigo-600 transition-colors"
              }`
            }
          >
            Outbox
          </NavLink>
          <NavLink
            to="/tapes/create"
            onClick={closeMenu}
            className={({ isActive }) =>
              `py-3 text-base border-t border-gray-100 ${
                isActive
                  ? "text-indigo-600 font-semibold"
                  : "text-gray-600 hover:text-indigo-600 transition-colors"
              }`
            }
          >
            New tape
          </NavLink>
          <div className="py-3 border-t border-gray-100 flex flex-col gap-2">
            <span className="text-sm text-gray-500">{user?.email}</span>
            <button
              onClick={() => {
                closeMenu();
                void handleLogout();
              }}
              className="self-start text-sm text-gray-500 hover:text-red-500 transition-colors"
            >
              Log out
            </button>
          </div>
        </div>
      )}
    </nav>
  );
}

export default Nav;