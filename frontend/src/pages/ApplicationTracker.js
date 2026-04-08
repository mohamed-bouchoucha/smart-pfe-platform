import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { applicationsAPI } from '../services/api';
import { FiClock, FiCheckCircle, FiXCircle, FiInfo, FiChevronRight } from 'react-icons/fi';
import { motion, AnimatePresence } from 'framer-motion';
import './ApplicationTracker.css';

const STAGES = [
  { id: 'interested', label: 'Intéressé', color: '#9ca3af' },
  { id: 'applied', label: 'Postulé', color: '#3b82f6' },
  { id: 'interview', label: 'Entretien', color: '#f59e0b' },
  { id: 'accepted', label: 'Accepté', color: '#10b981' },
  { id: 'rejected', label: 'Refusé', color: '#ef4444' },
];

export default function ApplicationTracker() {
  const { t } = useTranslation();
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchApplications = async () => {
    setLoading(true);
    try {
      const { data } = await applicationsAPI.list();
      setApplications(data.results || data);
    } catch (err) {
      console.error('Fetch applications error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApplications();
  }, []);

  const moveStatus = async (id, currentStatus) => {
    const currentIndex = STAGES.findIndex(s => s.id === currentStatus);
    if (currentIndex < STAGES.length - 2) { // Can move up to Accepted/Rejected
      const nextStatus = STAGES[currentIndex + 1].id;
      try {
        await applicationsAPI.updateStatus(id, nextStatus);
        fetchApplications();
      } catch (err) {
        console.error('Update status error:', err);
      }
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'accepted': return <FiCheckCircle className="text-success" />;
      case 'rejected': return <FiXCircle className="text-danger" />;
      case 'interview': return <FiClock className="text-warning" />;
      default: return <FiInfo className="text-info" />;
    }
  };

  return (
    <div className="application-tracker animate-fade-in">
      <div className="page-header">
        <h1>{t('common.application_tracker') || 'Suivi des Candidatures'}</h1>
        <p>{t('common.tracker_subtitle') || 'Gérez vos candidatures PFE étape par étape'}</p>
      </div>

      <div className="kanban-board">
        {STAGES.map((stage) => (
          <div key={stage.id} className="kanban-column">
            <div className="column-header" style={{ borderTop: `4px solid ${stage.color}` }}>
              <h3>{t(`common.status_${stage.id}`) || stage.label}</h3>
              <span className="count">
                {applications.filter(app => app.status === stage.id).length}
              </span>
            </div>

            <div className="column-content">
              <AnimatePresence mode="popLayout">
                {applications
                  .filter((app) => app.status === stage.id)
                  .map((app) => (
                    <motion.div
                      key={app.id}
                      layout
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, scale: 0.95 }}
                      className="application-card glass-card"
                    >
                      <div className="card-header">
                        {getStatusIcon(app.status)}
                        <span className="domain-badge">{app.project_details?.domain}</span>
                      </div>
                      <h4>{app.project_details?.title}</h4>
                      <p className="company">{app.project_details?.company_name}</p>
                      
                      <div className="card-footer">
                        <span className="date">{new Date(app.updated_at).toLocaleDateString()}</span>
                        {stage.id !== 'accepted' && stage.id !== 'rejected' && (
                          <button 
                            className="btn-next" 
                            onClick={() => moveStatus(app.id, app.status)}
                            title="Passer à l'étape suivante"
                          >
                            <FiChevronRight />
                          </button>
                        )}
                      </div>
                    </motion.div>
                  ))}
              </AnimatePresence>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
