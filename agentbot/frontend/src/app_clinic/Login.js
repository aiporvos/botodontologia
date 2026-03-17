import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await login(username, password);
      toast.success('¡Bienvenido!');
      navigate('/');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al iniciar sesión');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-500 to-primary-700">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-primary-500 rounded-full mx-auto mb-4 flex items-center justify-center">
            <span className="text-4xl">🦷</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Dental Studio Pro</h1>
          <p className="text-gray-600 mt-2">Inicia sesión para continuar</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Usuario
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="input-field"
              placeholder="admin"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Contraseña
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input-field"
              placeholder="••••••"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full btn-primary py-3 text-lg"
          >
            {loading ? 'Iniciando...' : 'Iniciar Sesión'}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-gray-500">
          <p>Demo: admin / admin123</p>
        </div>
      </div>
    </div>
  );
}

export default Login;
