import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Toaster } from 'react-hot-toast';
import Sidebar from './components/Sidebar/Sidebar';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Chatbot from './pages/Chatbot';
import Projects from './pages/Projects';
import Upload from './pages/Upload';
import Favorites from './pages/Favorites';
import AdminDashboard from './pages/AdminDashboard';
import HomePage from './pages/HomePage';
import ApplicationTracker from './pages/ApplicationTracker';
import Notifications from './pages/Notifications';
import './index.css';

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  if (loading) return <LoadingScreen />;
  return isAuthenticated ? children : <Navigate to="/login" />;
}

function AdminRoute({ children }) {
  const { isAuthenticated, isAdmin, loading } = useAuth();
  if (loading) return <LoadingScreen />;
  if (!isAuthenticated) return <Navigate to="/login" />;
  if (!isAdmin) return <Navigate to="/dashboard" />;
  return children;
}

function PublicRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  if (loading) return <LoadingScreen />;
  return isAuthenticated ? <Navigate to="/dashboard" /> : children;
}

function LoadingScreen() {
  return (
    <div style={{
      height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'var(--bg-primary)', color: 'var(--accent-primary-light)',
      fontSize: '1.2rem', fontWeight: 600,
    }}>
      ⏳ Chargement...
    </div>
  );
}

function AppLayout({ children }) {
  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">{children}</main>
    </div>
  );
}

function AppRoutes() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
      <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />

      {/* Protected Routes */}
      <Route path="/dashboard" element={
        <ProtectedRoute><AppLayout><Dashboard /></AppLayout></ProtectedRoute>
      } />
      <Route path="/chatbot" element={
        <ProtectedRoute><AppLayout><Chatbot /></AppLayout></ProtectedRoute>
      } />
      <Route path="/projects" element={
        <ProtectedRoute><AppLayout><Projects /></AppLayout></ProtectedRoute>
      } />
      <Route path="/upload" element={
        <ProtectedRoute><AppLayout><Upload /></AppLayout></ProtectedRoute>
      } />
      <Route path="/favorites" element={
        <ProtectedRoute><AppLayout><Favorites /></AppLayout></ProtectedRoute>
      } />
      <Route path="/applications" element={
        <ProtectedRoute><AppLayout><ApplicationTracker /></AppLayout></ProtectedRoute>
      } />
      <Route path="/notifications" element={
        <ProtectedRoute><AppLayout><Notifications /></AppLayout></ProtectedRoute>
      } />

      {/* Admin Routes */}
      <Route path="/admin" element={
        <AdminRoute><AppLayout><AdminDashboard /></AppLayout></AdminRoute>
      } />
      <Route path="/admin/users" element={
        <AdminRoute><AppLayout><AdminDashboard /></AppLayout></AdminRoute>
      } />
      <Route path="/admin/projects" element={
        <AdminRoute><AppLayout><AdminDashboard /></AppLayout></AdminRoute>
      } />

      {/* Home and catch-all */}
      <Route path="/" element={<HomePage />} />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <Toaster position="top-right" reverseOrder={false} />
        <AppRoutes />
      </AuthProvider>
    </Router>
  );
}

export default App;
