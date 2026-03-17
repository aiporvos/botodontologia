import { useEffect, useState } from 'react';
import { patientsAPI } from '../api/client';
import toast from 'react-hot-toast';

function Patients() {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    phone: '',
    dni: '',
    obra_social: 'Particular',
  });

  useEffect(() => {
    loadPatients();
  }, []);

  const loadPatients = async () => {
    try {
      const response = await patientsAPI.list({ limit: 50 });
      setPatients(response.data);
    } catch (error) {
      toast.error('Error al cargar pacientes');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await patientsAPI.create(formData);
      toast.success('Paciente creado exitosamente');
      setShowModal(false);
      setFormData({ first_name: '', last_name: '', phone: '', dni: '', obra_social: 'Particular' });
      loadPatients();
    } catch (error) {
      toast.error('Error al crear paciente');
    }
  };

  const filteredPatients = patients.filter(patient =>
    patient.first_name?.toLowerCase().includes(search.toLowerCase()) ||
    patient.last_name?.toLowerCase().includes(search.toLowerCase()) ||
    patient.dni?.includes(search) ||
    patient.phone?.includes(search)
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Pacientes</h1>
        <button onClick={() => setShowModal(true)} className="btn-primary">
          + Nuevo Paciente
        </button>
      </div>

      {/* Search */}
      <div className="glass-card p-4">
        <input
          type="text"
          placeholder="Buscar por nombre, DNI o teléfono..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="input-field"
        />
      </div>

      {/* Patients List */}
      <div className="glass-card overflow-hidden">
        {loading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500 mx-auto"></div>
          </div>
        ) : filteredPatients.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            No se encontraron pacientes
          </div>
        ) : (
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Nombre</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">DNI</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Teléfono</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Obra Social</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {filteredPatients.map((patient) => (
                <tr key={patient.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white font-bold">
                        {patient.first_name?.charAt(0)}{patient.last_name?.charAt(0)}
                      </div>
                      <span className="font-medium">{patient.full_name}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-gray-600">{patient.dni || '-'}</td>
                  <td className="px-6 py-4 text-gray-600">{patient.phone}</td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-1 bg-gray-100 rounded-full text-sm">
                      {patient.obra_social}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-2xl p-6 w-full max-w-lg">
            <h2 className="text-2xl font-bold mb-4">Nuevo Paciente</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
                  <input
                    type="text"
                    value={formData.first_name}
                    onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                    className="input-field"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Apellido</label>
                  <input
                    type="text"
                    value={formData.last_name}
                    onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                    className="input-field"
                    required
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Teléfono</label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData({...formData, phone: e.target.value})}
                  className="input-field"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">DNI</label>
                <input
                  type="text"
                  value={formData.dni}
                  onChange={(e) => setFormData({...formData, dni: e.target.value})}
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Obra Social</label>
                <input
                  type="text"
                  value={formData.obra_social}
                  onChange={(e) => setFormData({...formData, obra_social: e.target.value})}
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

export default Patients;
