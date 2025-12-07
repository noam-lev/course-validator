import { Outlet, RouterProvider, createBrowserRouter } from 'react-router-dom';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import NotFoundPage from './pages/NotFoundPage';
import Header from './components/Header';
import { AuthProvider } from './context/AuthContext';

const RootLayout = () => (
  <div className="min-h-screen bg-slate-950/90 text-white">
    <Header />
    <main className="mx-auto max-w-6xl px-4 pb-12 pt-6">
      <Outlet />
    </main>
  </div>
);

const router = createBrowserRouter([
  {
    element: <RootLayout />,
    children: [
      { path: '/', element: <HomePage /> },
      { path: '/login', element: <LoginPage /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
]);

const App = () => {
  return (
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  );
};

export default App;
