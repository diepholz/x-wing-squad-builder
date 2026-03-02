import { Link, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { useAuthStore } from "../../stores/authStore";
import AuthModal from "../auth/AuthModal";

export default function Header() {
  const { user, token, logout, fetchMe } = useAuthStore();
  const [showAuth, setShowAuth] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (token && !user) fetchMe();
  }, [token]);

  return (
    <>
      <header className="bg-gray-900 border-b border-gray-800 px-4 h-14 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <Link to="/" className="text-brand-500 font-bold text-lg tracking-wide">
            X-Wing Builder
          </Link>
          <nav className="flex gap-4 text-sm">
            <Link to="/build" className="text-gray-300 hover:text-white transition-colors">
              Builder
            </Link>
            {user && (
              <Link to="/squads" className="text-gray-300 hover:text-white transition-colors">
                My Squads
              </Link>
            )}
          </nav>
        </div>

        <div className="flex items-center gap-3">
          {user ? (
            <>
              <span className="text-gray-400 text-sm">{user.username}</span>
              <button
                onClick={() => { logout(); navigate("/"); }}
                className="text-sm text-gray-400 hover:text-white transition-colors"
              >
                Sign out
              </button>
            </>
          ) : (
            <button
              onClick={() => setShowAuth(true)}
              className="text-sm bg-brand-600 hover:bg-brand-500 text-white px-3 py-1.5 rounded transition-colors"
            >
              Sign in
            </button>
          )}
        </div>
      </header>

      {showAuth && <AuthModal onClose={() => setShowAuth(false)} />}
    </>
  );
}
