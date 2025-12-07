import { Link } from 'react-router-dom';

const NotFoundPage = () => {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 text-white shadow-lg">
      <h1 className="text-xl font-semibold">Page not found</h1>
      <p className="mt-2 text-sm text-slate-300">
        The page you are looking for does not exist. Go back home to analyze an idea.
      </p>
      <Link
        to="/"
        className="mt-4 inline-block rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white"
      >
        Back to Home
      </Link>
    </div>
  );
};

export default NotFoundPage;

