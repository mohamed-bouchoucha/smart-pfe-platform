import React, { useState, useEffect } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../context/AuthContext';
import { notificationsAPI } from '../../services/api';
import {
  FiHome, FiMessageSquare, FiFolder, FiUpload,
  FiHeart, FiLogOut, FiUsers, FiBarChart2, FiCpu,
  FiGlobe, FiColumns, FiCalendar
} from 'react-icons/fi';
import './Sidebar.css';

export default function Sidebar() {
  const { user, logout, isAdmin } = useAuth();
  const [unreadCount, setUnreadCount] = useState(0);
  const { t, i18n } = useTranslation();
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

  const toggleLanguage = () => {
    const newLang = i18n.language === 'fr' ? 'en' : 'fr';
    i18n.changeLanguage(newLang);
  };

  const studentLinks = [
    { to: '/dashboard', icon: <FiHome />, label: t('common.dashboard'), badge: unreadCount > 0 ? unreadCount : null },
    { to: '/chatbot', icon: <FiMessageSquare />, label: 'Chatbot IA' },
    { to: '/projects', icon: <FiFolder />, label: t('common.projects') || t('common.catalog') },
    { to: '/upload', icon: <FiUpload />, label: t('common.documents') || 'Documents' },
    { to: '/favorites', icon: <FiHeart />, label: t('common.favorites') },
    { to: '/applications', icon: <FiColumns />, label: t('common.tracker') || 'Tracker' },
  ];

  const adminLinks = [
    { to: '/admin', icon: <FiBarChart2 />, label: t('admin.statistics') },
    { to: '/admin/users', icon: <FiUsers />, label: t('admin.users') },
    { to: '/admin/projects', icon: <FiFolder />, label: t('admin.projects') },
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
          <span className="nav-section-title">{t('common.main_menu') || 'MENU PRINCIPAL'}</span>
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
            <span className="nav-section-title">{t('common.administration')}</span>
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
        <div className="lang-switcher-wrapper">
          <button className="lang-toggle-btn" onClick={toggleLanguage} title={i18n.language === 'fr' ? 'Switch to English' : 'Passer au Français'}>
            <FiGlobe />
            <span>{i18n.language.toUpperCase()}</span>
          </button>
        </div>

        <div className="footer-user-row">
          <div className="user-info">
            <div className="user-avatar" title={user?.email}>
              {user?.first_name?.[0] || user?.username?.[0] || '?'}
            </div>
            <div className="user-details">
              <span className="user-name">{user?.first_name || user?.username}</span>
              <span className="user-role">{isAdmin ? 'Admin' : t('auth.student') || 'Étudiant'}</span>
            </div>
          </div>
          <button onClick={handleLogout} className="btn-ghost nav-link logout-btn" title={t('common.logout')}>
            <FiLogOut />
          </button>
        </div>
      </div>
    </aside>
  );
}
