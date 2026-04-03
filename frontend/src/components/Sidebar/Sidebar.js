import React, { useState, useEffect } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { notificationsAPI } from '../../services/api';
import {
  FiHome, FiMessageSquare, FiFolder, FiUpload,
  FiHeart, FiLogOut, FiUsers, FiBarChart2, FiCpu,
  FiBell
} from 'react-icons/fi';
import './Sidebar.css';

export default function Sidebar() {
  const { user, logout, isAdmin } = useAuth();
  const [unreadCount, setUnreadCount] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    if (user) {
      fetchNotifications();
    }
  }, [user]);

  const fetchNotifications = async () => {
    try {
      const { data } = await notificationsAPI.list();
      const unread = (data.results || data || []).filter(n => !n.is_read).length;
      setUnreadCount(unread);
    } catch (err) {
      console.error('Fetch notifications count error:', err);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const studentLinks = [
    { to: '/dashboard', icon: <FiHome />, label: 'Dashboard', badge: unreadCount > 0 ? unreadCount : null },
    { to: '/chatbot', icon: <FiMessageSquare />, label: 'Chatbot IA' },
    { to: '/projects', icon: <FiFolder />, label: 'Projets' },
    { to: '/upload', icon: <FiUpload />, label: 'Documents' },
    { to: '/favorites', icon: <FiHeart />, label: 'Favoris' },
  ];

  const adminLinks = [
    { to: '/admin', icon: <FiBarChart2 />, label: 'Statistiques' },
    { to: '/admin/users', icon: <FiUsers />, label: 'Utilisateurs' },
    { to: '/admin/projects', icon: <FiFolder />, label: 'Projets' },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <FiCpu className="logo-icon" />
          <span>Smart PFE</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-section">
          <span className="nav-section-title">MENU PRINCIPAL</span>
          {studentLinks.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              <div className="nav-icon-wrapper">
                {link.icon}
                {link.badge && <span className="nav-badge">{link.badge}</span>}
              </div>
              <span>{link.label}</span>
            </NavLink>
          ))}
        </div>

        {isAdmin && (
          <div className="nav-section">
            <span className="nav-section-title">ADMINISTRATION</span>
            {adminLinks.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
              >
                {link.icon}
                <span>{link.label}</span>
              </NavLink>
            ))}
          </div>
        )}
      </nav>

      <div className="sidebar-footer">
        <div className="user-info">
          <div className="user-avatar" title={user?.email}>
            {user?.first_name?.[0] || user?.username?.[0] || '?'}
          </div>
          <div className="user-details">
            <span className="user-name">{user?.first_name || user?.username}</span>
            <span className="user-role">{isAdmin ? 'Admin' : 'Étudiant'}</span>
          </div>
        </div>
        <button onClick={handleLogout} className="btn-ghost nav-link logout-btn" title="Déconnexion">
          <FiLogOut />
        </button>
      </div>
    </aside>
  );
}
