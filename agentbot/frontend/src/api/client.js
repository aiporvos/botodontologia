import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token expiration
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;

// Auth API
export const authAPI = {
  login: (username, password) =>
    apiClient.post('/auth/login', { username, password }),
  me: () => apiClient.get('/auth/me'),
};

// Patients API
export const patientsAPI = {
  list: (params) => apiClient.get('/admin/patients/', { params }),
  create: (data) => apiClient.post('/admin/patients/', data),
  update: (id, data) => apiClient.put(`/admin/patients/${id}`, data),
  delete: (id) => apiClient.delete(`/admin/patients/${id}`),
};

// Appointments API
export const appointmentsAPI = {
  list: (params) => apiClient.get('/admin/appointments/', { params }),
  today: () => apiClient.get('/admin/appointments/today'),
  create: (data) => apiClient.post('/admin/appointments/', data),
  update: (id, data) => apiClient.put(`/admin/appointments/${id}`, data),
  cancel: (id, reason) => apiClient.put(`/admin/appointments/${id}/cancel`, { reason }),
};

// Professionals API
export const professionalsAPI = {
  list: () => apiClient.get('/public/professionals'),
};
