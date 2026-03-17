import { useEffect, useState } from 'react';
import { appointmentsAPI, professionalsAPI } from '../api/client';
import { format, addDays, startOfWeek } from 'date-fns';
import { es } from 'date-fns/locale';
import toast from 'react-hot-toast';

function Schedule() {
  const [appointments, setAppointments] = useState([]);
  const [professionals, setProfessionals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    patient_id: '',
    professional_id: '',
    start_at: '',
    end_at: '',
    reason: '',
    category: 'consulta',
  });

  useEffect(() => {
    loadData();
  }, [selectedDate]);

  const loadData = async () => {
    try {
      const [appointmentsRes, professionalsRes] = await Promise.all([
        appointmentsAPI.list({
          start_date: format(selectedDate, 'yyyy-MM-dd'),
          end_date: format(addDays(selectedDate, 1), 'yyyy-MM-dd'),
        }),
        professionalsAPI.list(),
      ]);
      setAppointments(appointmentsRes.data);
      setProfessionals(professionalsRes.data);
    } catch (error) {
      toast.error('Error al cargar agenda');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await appointmentsAPI.create(formData);
      toast.success('Turno creado exitosamente');
      setShowModal(false);
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al crear turno');
    }
  };

  const weekDays = Array.from({ length: 7 }, (_, i) => 
    addDays(startOfWeek(selectedDate, { locale: es }), i)
  );

  const timeSlots = Array.from({ length: 24 }, (_, i) => i);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Agenda</h1>
        <button onClick={() => setShowModal(true)} className="btn-primary">
          + Nuevo Turno
        </button>
      </div>

      {/* Calendar View */}
      <div className="glass-card">
        <div className="p-4 border-b">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSelectedDate(addDays(selectedDate, -7))}
              className="p-2 hover:bg-gray-100 rounded-lg"
            >
              ←
            </button>
            <h2 className="text-lg font-semibold">
              {format(startOfWeek(selectedDate, { locale: es }), "MMMM yyyy", { locale: es })}
            </h2>
            <button
              onClick={() => setSelectedDate(addDays(selectedDate, 7))}
              className="p-2 hover:bg-gray-100 rounded-lg"
            >
              →
            </button>
          </div>
        </div>

        {loading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500 mx-auto"></div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr>
                  <th className="p-4 text-left border-b">Hora</th>
                  {weekDays.map((day) => (
                    <th key={day} className="p-4 text-center border-b min-w-[120px]">
                      <div className={format(day, 'yyyy-MM-dd') === format(new Date(), 'yyyy-MM-dd') ? 'text-primary-600 font-bold' : ''}>
                        <div className="text-sm text-gray-500">{format(day, 'EEE', { locale: es })}</div>
                        <div className="text-lg">{format(day, 'd')}</div>
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {timeSlots.filter(hour => hour >= 8 && hour <= 20).map((hour) => (
                  <tr key={hour} className="border-b">
                    <td className="p-4 text-sm text-gray-500 font-medium">
                      {hour}:00
                    </td>
                    {weekDays.map((day) => {
                      const dayAppointments = appointments.filter(apt => {
                        const aptDate = new Date(apt.start_at);
                        return format(aptDate, 'yyyy-MM-dd') === format(day, 'yyyy-MM-dd') &&
                               aptDate.getHours() === hour;
                      });
                      
                      return (
                        <td key={day} className="p-2 border-l">
                          {dayAppointments.map(apt => (
                            <div
                              key={apt.id}
                              className={`p-2 rounded-lg text-sm ${
                                apt.status === 'confirmed' ? 'bg-green-100 text-green-800' :
                                apt.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                                'bg-gray-100 text-gray-800'
                              }`}
                            >
                              <div className="font-medium">{apt.patient_name}</div>
                              <div className="text-xs">{apt.reason || 'Consulta'}</div>
                            </div>
                          ))}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-2xl p-6 w-full max-w-lg">
            <h2 className="text-2xl font-bold mb-4">Nuevo Turno</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Paciente ID</label>
                <input
                  type="number"
                  value={formData.patient_id}
                  onChange={(e) => setFormData({...formData, patient_id: e.target.value})}
                  className="input-field"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Profesional</label>
                <select
                  value={formData.professional_id}
                  onChange={(e) => setFormData({...formData, professional_id: e.target.value})}
                  className="input-field"
                  required
                >
                  <option value="">Seleccionar...</option>
                  {professionals.map((prof) => (
                    <option key={prof.id} value={prof.id}>
                      {prof.full_name} - {prof.specialty}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Fecha y Hora</label>
                <input
                  type="datetime-local"
                  value={formData.start_at}
                  onChange={(e) => {
                    const start = e.target.value;
                    const end = new Date(new Date(start).getTime() + 30 * 60000).toISOString().slice(0, 16);
                    setFormData({...formData, start_at: start, end_at: end});
                  }}
                  className="input-field"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Motivo</label>
                <input
                  type="text"
                  value={formData.reason}
                  onChange={(e) => setFormData({...formData, reason: e.target.value})}
                  className="input-field"
                />
              </div>
              <div className="flex gap-4 pt-4">
                <button type="button" onClick={() => setShowModal(false)} className="flex-1 btn-secondary">
                  Cancelar
                </button>
                <button type="submit" className="flex-1 btn-primary">
                  Guardar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default Schedule;
