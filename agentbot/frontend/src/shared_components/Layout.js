import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function Layout() {
  const { user, logout } = useAuth();
  const location = useLocation();

  const menuItems = [
    { path: '/', label: 'Dashboard', icon: '📊' },
    { path: '/patients', label: 'Pacientes', icon: '👥' },
    { path: '/schedule', label: 'Agenda', icon: '📅' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 h-full w-64 bg-white shadow-lg z-50">
        <div className="p-6 border-b">
          <h1 className="text-2xl font-bold text-primary-500">Dental Studio</h1>
          <p className="text-sm text-gray-500">Sistema de Gestión</p>
        </div>
        
        <nav className="p-4 space-y-2">
          {menuItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`sidebar-link ${
                location.pathname === item.path ? 'active' : ''
              }`}
            >
              <span className="text-xl">{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 p-4 border-t">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-full bg-primary-500 flex items-center justify-center text-white font-bold">
              {user?.full_name?.charAt(0) || 'U'}
            </div>
            <div>
              <p className="font-medium text-gray-900">{user?.full_name || 'Usuario'}</p>
              <p className="text-sm text-gray-500 capitalize">{user?.role}</p>
            </div>
          </div>
          <button
            onClick={logout}
            className="w-full py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
          >
            Cerrar Sesión
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="ml-64 p-8">
        <Outlet />
      </main>
    </div>
  );
}

export default Layout;
