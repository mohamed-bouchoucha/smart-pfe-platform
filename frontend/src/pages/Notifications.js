import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { notificationsAPI } from '../services/api';
import { FiBell, FiCheck, FiInfo, FiAlertCircle, FiTrash2, FiClock } from 'react-icons/fi';
import { toast } from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';
import './Notifications.css';

export default function Notifications() {
  const { t } = useTranslation();
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const { data } = await notificationsAPI.list();
      setNotifications(data.results || data || []);
    } catch (err) {
      console.error('Fetch notifications error:', err);
      toast.error(t('notifications.fetch_error') || 'Erreur lors du chargement des notifications.');
    } finally {
      setLoading(false);
    }
  };

  const handleMarkRead = async (id) => {
    try {
      await notificationsAPI.markRead(id);
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n));
    } catch (err) {
      toast.error(t('notifications.mark_read_error') || 'Erreur.');
    }
  };

  const handleDelete = async (id) => {
    try {
      // Logic for backend deletion if endpoint exists
      if (notificationsAPI.delete) {
        await notificationsAPI.delete(id);
      }
      setNotifications(prev => prev.filter(n => n.id !== id));
      toast.success(t('common.deleted') || 'Notification supprimée');
    } catch (err) {
      console.error('Delete notification error:', err);
      toast.error(t('notifications.delete_error') || 'Erreur lors de la suppression.');
    }
  };

  const getIcon = (type) => {
    switch (type) {
      case 'success': return <FiCheck />;
      case 'warning': return <FiAlertCircle />;
      default: return <FiInfo />;
    }
  };

  return (
    <div className="notifications-page animate-fade-in">
      <div className="notifications-header">
        <div>
          <h1>{t('common.notifications') || 'Notifications'}</h1>
          <p>{t('notifications.subtitle') || 'Suivez les mises à jour de vos projets et candidatures'}</p>
        </div>
        <div className="notifications-controls">
          <button className="btn btn-secondary" onClick={fetchNotifications}>
            {t('common.refresh') || 'Actualiser'}
          </button>
        </div>
      </div>

      {loading ? (
        <div className="loading-state">{t('common.loading')}</div>
      ) : (
        <div className="notifications-list">
          <AnimatePresence mode="popLayout">
            {notifications.length > 0 ? (
              notifications.map((n) => (
                <motion.div
                  key={n.id}
                  layout
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  className={`glass-card notification-item ${!n.is_read ? 'unread' : ''}`}
                >
                  <div className={`notification-icon ${n.type || 'info'}`}>
                    {getIcon(n.type)}
                  </div>
                  <div className="notification-content">
                    <h4>{n.title}</h4>
                    <p>{n.message}</p>
                    <div className="notification-time">
                      <FiClock /> {new Date(n.created_at).toLocaleString()}
                    </div>
                  </div>
                  <div className="notification-actions">
                    {!n.is_read && (
                      <button 
                        className="btn-icon success" 
                        onClick={() => handleMarkRead(n.id)}
                        title={t('notifications.mark_read') || 'Marquer comme lu'}
                      >
                        <FiCheck />
                      </button>
                    )}
                    <button 
                      className="btn-icon danger" 
                      onClick={() => handleDelete(n.id)}
                      title={t('common.delete')}
                    >
                      <FiTrash2 />
                    </button>
                  </div>
                </motion.div>
              ))
            ) : (
              <div className="empty-notifications glass-card">
                <FiBell />
                <p>{t('notifications.empty') || 'Aucune notification pour le moment.'}</p>
              </div>
            )}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
}
