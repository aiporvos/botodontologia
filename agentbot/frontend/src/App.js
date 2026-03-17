import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Login from './app_clinic/Login';
import Dashboard from './app_clinic/Dashboard';
import Patients from './app_clinic/Patients';
import Schedule from './app_clinic/Schedule';
import Layout from './shared_components/Layout';

function PrivateRoute({ children }) {
  const { token } = useAuth();
  return token ? children : <Navigate to="/login" />;
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={
        <PrivateRoute>
          <Layout />
        </PrivateRoute>
      }>
        <Route index element={<Dashboard />} />
        <Route path="patients" element={<Patients />} />
        <Route path="schedule" element={<Schedule />} />
      </Route>
    </Routes>
  );
}

export default App;
