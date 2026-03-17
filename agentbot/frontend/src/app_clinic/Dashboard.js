import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { appointmentsAPI, patientsAPI } from '../api/client';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

function Dashboard() {
  const [stats, setStats] = useState({
    todayAppointments: 0,
    totalPatients: 0,
    pendingAppointments: 0,
    weeklyAppointments: 0,
  });
  const [todayAppointments, setTodayAppointments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [todayRes, patientsRes] = await Promise.all([
        appointmentsAPI.today(),
        patientsAPI.list({ limit: 1 }),
      ]);

      setTodayAppointments(todayRes.data);
      setStats({
        todayAppointments: todayRes.data.length,
        totalPatients: patientsRes.data.length, // Esto debería venir de un endpoint de stats
        pendingAppointments: todayRes.data.filter(a => a.status === 'pending').length,
        weeklyAppointments: 0, // Placeholder
      });
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    { label: 'Turnos Hoy', value: stats.todayAppointments, color: 'bg-blue-500' },
    { label: 'Pacientes', value: stats.totalPatients, color: 'bg-green-500' },
    { label: 'Pendientes', value: stats.pendingAppointments, color: 'bg-orange-500' },
    { label: 'Esta Semana', value: stats.weeklyAppointments, color: 'bg-purple-500' },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">
            {format(new Date(), "EEEE d 'de' MMMM, yyyy", { locale: es })}
          </p>
        </div>
        <Link to="/schedule" className="btn-primary">
          + Nuevo Turno
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => (
          <div key={index} className="glass-card p-6">
            <div className={`w-12 h-12 ${stat.color} rounded-lg flex items-center justify-center text-white text-2xl mb-4`}>
              📊
            </div>
            <p className="text-gray-600 text-sm">{stat.label}</p>
            <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
          </div>
        ))}
      </div>

      {/* Today's Appointments */}
      <div className="glass-card">
        <div className="p-6 border-b">
          <h2 className="text-xl font-bold text-gray-900">Turnos de Hoy</h2>
        </div>
        
        {todayAppointments.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <p className="text-lg">No hay turnos programados para hoy</p>
            <Link to="/schedule" className="text-primary-500 hover:underline mt-2 inline-block">
              Programar uno
            </Link>
          </div>
        ) : (
          <div className="divide-y">
            {todayAppointments.map((appointment) => (
              <div key={appointment.id} className="p-4 hover:bg-gray-50 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 font-bold">
                    {format(new Date(appointment.start_at), 'HH:mm')}
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900">{appointment.patient_name}</p>
                    <p className="text-sm text-gray-600">{appointment.reason || 'Consulta'}</p>
                    <p className="text-sm text-gray-500">{appointment.professional_name}</p>
                  </div>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  appointment.status === 'confirmed' ? 'bg-green-100 text-green-800' :
                  appointment.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {appointment.status === 'confirmed' ? 'Confirmado' :
                   appointment.status === 'pending' ? 'Pendiente' : 'Cancelado'}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
