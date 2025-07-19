import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './components/Login';
import AdminLogin from './components/AdminLogin';
import Dashboard from './components/Dashboard';
import AdminDashboard from './components/AdminDashboard';
import Results from './components/Results';
import './App.css';

// Composant de protection des routes
const ProtectedRoute = ({ children, requireAdmin = false }) => {
  const { user, admin, loading } = useAuth();
  
  if (loading) {
    return <div className="loading">Chargement...</div>;
  }
  
  if (requireAdmin) {
    return admin ? children : <Navigate to="/admin/login" />;
  }
  
  return user ? children : <Navigate to="/login" />;
};

// Composant de protection des routes publiques
const PublicRoute = ({ children, redirectTo = "/dashboard" }) => {
  const { user, admin, loading } = useAuth();
  
  if (loading) {
    return <div className="loading">Chargement...</div>;
  }
  
  if (user) {
    return <Navigate to={redirectTo} />;
  }
  
  if (admin) {
    return <Navigate to="/admin/dashboard" />;
  }
  
  return children;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            {/* Routes publiques */}
            <Route path="/" element={<Navigate to="/login" />} />
            
            {/* Route de connexion étudiant */}
            <Route 
              path="/login" 
              element={
                <PublicRoute>
                  <Login />
                </PublicRoute>
              } 
            />
            
            {/* Route de connexion administrateur */}
            <Route 
              path="/admin/login" 
              element={
                <PublicRoute redirectTo="/admin/dashboard">
                  <AdminLogin />
                </PublicRoute>
              } 
            />
            
            {/* Routes protégées étudiant */}
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/results" 
              element={
                <ProtectedRoute>
                  <Results />
                </ProtectedRoute>
              } 
            />
            
            {/* Routes protégées administrateur */}
            <Route 
              path="/admin/dashboard" 
              element={
                <ProtectedRoute requireAdmin={true}>
                  <AdminDashboard />
                </ProtectedRoute>
              } 
            />
            
            {/* Route 404 */}
            <Route path="*" element={<Navigate to="/login" />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App; 