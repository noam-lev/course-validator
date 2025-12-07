import { Link, useLocation } from 'react-router-dom';
import { APP_NAME } from '../config';
import { useAuth } from '../context/AuthContext';

const Header = () => {
  const location = useLocation();
  const { isLoggedIn, username, login, logout } = useAuth();

  const isActive = (path: string) =>
    location.pathname === path ? 'text-white' : 'text-slate-300';

  return (
    <header className="sticky top-0 z-10 border-b border-slate-800 bg-slate-950/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
        <Link to="/" className="text-lg font-semibold text-white">
          {APP_NAME}
        </Link>
        <nav className="flex items-center gap-4 text-sm">
          <Link className={isActive('/')} to="/">
            Home
          </Link>
          <Link className={isActive('/login')} to="/login">
            Login
          </Link>
          {isLoggedIn ? (
            <div className="flex items-center gap-3 rounded-full border border-slate-800 bg-slate-900/70 px-3 py-1 text-slate-100">
              <span className="text-xs uppercase tracking-wide text-indigo-300">
                {username}
              </span>
              <button
                type="button"
                className="rounded-full bg-slate-800 px-3 py-1 text-xs font-semibold text-indigo-200"
                onClick={logout}
              >
                Logout
              </button>
            </div>
          ) : (
            <button
              type="button"
              className="rounded-full bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow"
              onClick={() => login()}
            >
              Mock Login
            </button>
          )}
        </nav>
      </div>
    </header>
  );
};

export default Header;

