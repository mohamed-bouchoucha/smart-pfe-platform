import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { adminAPI, authAPI, projectsAPI } from '../services/api';
import { FiUsers, FiFolder, FiMessageSquare, FiActivity, FiCheck, FiX, FiUserPlus, FiShield, FiUser } from 'react-icons/fi';
import { toast } from 'react-hot-toast';
import './Admin.css';

export default function AdminDashboard() {
  const { t, i18n } = useTranslation();
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [projects, setProjects] = useState([]);
  const [supervisors, setSupervisors] = useState([]);
  const [activeTab, setActiveTab] = useState('stats');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchData();
  }, [i18n.language]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [statsRes, usersRes, projectsRes, supervisorsRes] = await Promise.allSettled([
        adminAPI.getStats(),
        authAPI.getUsers(),
        projectsAPI.list(),
        authAPI.getSupervisors(),
      ]);

      if (statsRes.status === 'fulfilled') setStats(statsRes.value.data);
      if (usersRes.status === 'fulfilled') setUsers(usersRes.value.data.results || usersRes.value.data || []);
      if (projectsRes.status === 'fulfilled') setProjects(projectsRes.value.data.results || projectsRes.value.data || []);
      if (supervisorsRes.status === 'fulfilled') setSupervisors(supervisorsRes.value.data.results || supervisorsRes.value.data || []);
    } catch (err) {
      console.error('Admin fetch error:', err);
      toast.error(t('admin.fetch_error') || 'Erreur lors du chargement des données.');
    } finally {
      setLoading(false);
    }
  };

  const handleProjectStatus = async (id, status) => {
    try {
      await projectsAPI.validate(id, status);
      toast.success(t('admin.project_status_updated') || `Projet ${status === 'validated' ? 'validé' : 'rejeté'}`);
      fetchData();
    } catch (err) {
      toast.error(t('admin.status_error') || 'Erreur lors du changement de statut.');
    }
  };

  const handleAssignSupervisor = async (projectId, supervisorId) => {
    try {
      await projectsAPI.assign(projectId, supervisorId);
      toast.success(t('admin.assign_success') || 'Encadrant assigné avec succès.');
      fetchData();
    } catch (err) {
      toast.error(t('admin.assign_error') || "Erreur lors de l'assignation.");
    }
  };

  const handleToggleUserActive = async (userId) => {
    try {
      await authAPI.toggleActive(userId);
      toast.success(t('admin.user_status_updated') || 'Statut utilisateur mis à jour.');
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || t('admin.status_error'));
    }
  };

  const handleChangeRole = async (userId, newRole) => {
    try {
      await authAPI.updateUser(userId, { role: newRole });
      toast.success(`${t('admin.role_updated') || 'Rôle mis à jour'} : ${newRole}`);
      fetchData();
    } catch (err) {
      toast.error(t('admin.role_error') || 'Erreur lors du changement de rôle.');
    }
  };

  return (
    <div className="admin-page animate-fade-in">
      <div className="page-header">
        <h1>{t('common.administration')}</h1>
        <p>{t('admin.subtitle') || 'Gérez la plateforme Smart PFE'}</p>
      </div>

      {/* Tabs */}
      <div className="admin-tabs">
        {[
          { key: 'stats', label: t('admin.statistics'), icon: <FiActivity /> },
          { key: 'users', label: t('admin.users'), icon: <FiUsers /> },
          { key: 'projects', label: t('admin.projects'), icon: <FiFolder /> },
        ].map((tab) => (
          <button
            key={tab.key}
            className={`tab-btn ${activeTab === tab.key ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.key)}
          >
            {tab.icon} {tab.label}
          </button>
        ))}
      </div>

      {loading && <div className="loading-overlay">{t('common.loading')}</div>}

      {/* Stats Tab */}
      {activeTab === 'stats' && stats && (
        <div className="stats-content">
          <div className="grid grid-4">
            <div className="glass-card stat-card">
              <div className="stat-icon purple"><FiUsers /></div>
              <div className="stat-info">
                <h3>{stats.users?.total || 0}</h3>
                <p>{t('admin.users')}</p>
              </div>
            </div>
            <div className="glass-card stat-card">
              <div className="stat-icon cyan"><FiFolder /></div>
              <div className="stat-info">
                <h3>{stats.projects?.total || 0}</h3>
                <p>{t('admin.projects')}</p>
              </div>
            </div>
            <div className="glass-card stat-card">
              <div className="stat-icon green"><FiMessageSquare /></div>
              <div className="stat-info">
                <h3>{stats.conversations?.total || 0}</h3>
                <p>{t('common.conversations')}</p>
              </div>
            </div>
            <div className="glass-card stat-card">
              <div className="stat-icon orange"><FiActivity /></div>
              <div className="stat-info">
                <h3>{stats.users?.active_today || 0}</h3>
                <p>{t('admin.active_today')}</p>
              </div>
            </div>
          </div>

          <div className="glass-card domain-stats-card">
            <h3>{t('admin.projects_by_domain')}</h3>
            <div className="domain-stats">
              {stats.projects?.by_domain && Object.entries(stats.projects.by_domain).map(([domain, count]) => (
                <div key={domain} className="domain-bar">
                  <span className="domain-label">{domain}</span>
                  <div className="domain-bar-bg">
                    <div
                      className="domain-bar-fill"
                      style={{ width: `${Math.min((count / (stats.projects?.total || 1)) * 100, 100)}%` }}
                    ></div>
                  </div>
                  <span className="domain-count">{count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Users Tab */}
      {activeTab === 'users' && (
        <div className="glass-card table-section">
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>{t('admin.user_header')}</th>
                  <th>{t('admin.role_header')}</th>
                  <th>{t('admin.university_header')}</th>
                  <th>{t('admin.status_header')}</th>
                  <th>{t('admin.actions_header')}</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id}>
                    <td>
                      <div className="user-cell">
                        <span className="user-initials">{u.first_name?.[0]}{u.last_name?.[0]}</span>
                        <div className="user-meta">
                          <span className="user-full-name">{u.first_name} {u.last_name}</span>
                          <span className="user-email">{u.email}</span>
                        </div>
                      </div>
                    </td>
                    <td>
                      <select 
                        className="role-select" 
                        value={u.role} 
                        onChange={(e) => handleChangeRole(u.id, e.target.value)}
                      >
                        <option value="student">{t('auth.student')}</option>
                        <option value="supervisor">{t('auth.supervisor')}</option>
                        <option value="admin">{t('auth.admin')}</option>
                      </select>
                    </td>
                    <td>{u.university || '—'}</td>
                    <td>
                      <span className={`badge badge-${u.is_active ? 'success' : 'danger'}`}>
                        {u.is_active ? t('admin.active') : t('admin.inactive')}
                      </span>
                    </td>
                    <td>
                      <button 
                        className={`btn btn-sm ${u.is_active ? 'btn-danger' : 'btn-success'}`}
                        onClick={() => handleToggleUserActive(u.id)}
                      >
                        {u.is_active ? t('admin.deactivate') : t('admin.activate')}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Projects Tab */}
      {activeTab === 'projects' && (
        <div className="glass-card table-section">
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>{t('admin.project_title_header')}</th>
                  <th>{t('admin.domain_diff_header')}</th>
                  <th>{t('common.supervisor')}</th>
                  <th>{t('admin.status_header')}</th>
                  <th>{t('admin.actions_header')}</th>
                </tr>
              </thead>
              <tbody>
                {projects.map((p) => (
                  <tr key={p.id}>
                    <td>
                      <div className="project-cell">
                        <span className="project-title">{p.title}</span>
                        <span className="project-owner">By {p.created_by_name}</span>
                      </div>
                    </td>
                    <td>
                      <div className="tags-cell">
                        <span className="badge badge-info">{p.domain}</span>
                        <span className={`badge badge-${p.difficulty === 'beginner' ? 'success' : p.difficulty === 'intermediate' ? 'warning' : 'danger'}`}>
                          {p.difficulty}
                        </span>
                      </div>
                    </td>
                    <td>
                      <select 
                        className="supervisor-select"
                        value={p.supervisor || ''}
                        onChange={(e) => handleAssignSupervisor(p.id, e.target.value)}
                      >
                        <option value="">{t('admin.not_assigned')}</option>
                        {supervisors.map(s => (
                          <option key={s.id} value={s.id}>M. {s.last_name}</option>
                        ))}
                      </select>
                    </td>
                    <td>
                      <span className={`badge badge-${p.status === 'validated' || p.status === 'approved' ? 'success' : p.status === 'rejected' ? 'danger' : 'warning'}`}>
                        {p.status}
                      </span>
                    </td>
                    <td>
                      <div className="action-btns">
                        {(p.status === 'proposed' || p.status === 'rejected') && (
                          <button className="btn-icon success" title={t('admin.approve') || 'Approuver'} onClick={() => handleProjectStatus(p.id, 'approved')}>
                            <FiCheck />
                          </button>
                        )}
                        {p.status !== 'rejected' && (
                          <button className="btn-icon danger" title={t('admin.reject') || 'Rejeter'} onClick={() => handleProjectStatus(p.id, 'rejected')}>
                            <FiX />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
