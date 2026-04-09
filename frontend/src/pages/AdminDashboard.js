import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { adminAPI, authAPI, projectsAPI } from '../services/api';
import { FiUsers, FiFolder, FiMessageSquare, FiActivity, FiCheck, FiX, FiUserPlus, FiShield, FiUser, FiPieChart, FiBarChart } from 'react-icons/fi';
import { Doughnut, Bar, PolarArea, Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  RadialLinearScale,
} from 'chart.js';
import { toast } from 'react-hot-toast';
import './Admin.css';

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  RadialLinearScale
);

export default function AdminDashboard() {
  const { t, i18n } = useTranslation();
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [projects, setProjects] = useState([]);
  const [supervisors, setSupervisors] = useState([]);
  const [activeTab, setActiveTab] = useState('stats');
  const [loading, setLoading] = useState(false);
  const [advStats, setAdvStats] = useState(null);

  useEffect(() => {
    fetchData();
  }, [i18n.language]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [statsRes, usersRes, projectsRes, supervisorsRes, advStatsRes] = await Promise.allSettled([
        adminAPI.getStats(),
        authAPI.getUsers(),
        projectsAPI.list(),
        authAPI.getSupervisors(),
        projectsAPI.getStatistics(),
      ]);

      if (statsRes.status === 'fulfilled') setStats(statsRes.value.data);
      if (usersRes.status === 'fulfilled') setUsers(usersRes.value.data.results || usersRes.value.data || []);
      if (projectsRes.status === 'fulfilled') setProjects(projectsRes.value.data.results || projectsRes.value.data || []);
      if (supervisorsRes.status === 'fulfilled') setSupervisors(supervisorsRes.value.data.results || supervisorsRes.value.data || []);
      if (advStatsRes.status === 'fulfilled') setAdvStats(advStatsRes.value.data);
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

          <div className="charts-grid mt-4">
            {/* Project Domains */}
            <div className="glass-card chart-card">
              <h3><FiPieChart /> {t('admin.projects_by_domain')}</h3>
              <div className="chart-container">
                <Doughnut 
                  data={{
                    labels: advStats?.projects_by_domain.map(d => d.domain) || [],
                    datasets: [{
                      data: advStats?.projects_by_domain.map(d => d.count) || [],
                      backgroundColor: ['#6366f1', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'],
                      borderWidth: 0,
                    }]
                  }}
                  options={{ plugins: { legend: { position: 'bottom', labels: { color: '#9ca3af' } } } }}
                />
              </div>
            </div>

            {/* Application Stages */}
            <div className="glass-card chart-card">
              <h3><FiActivity /> {t('admin.application_pipeline') || 'Pipeline des Candidatures'}</h3>
              <div className="chart-container">
                <Bar 
                  data={{
                    labels: advStats?.applications_by_status.map(s => s.status) || [],
                    datasets: [{
                      label: t('admin.count') || 'Nombre',
                      data: advStats?.applications_by_status.map(s => s.count) || [],
                      backgroundColor: '#6366f1',
                      borderRadius: 6,
                    }]
                  }}
                  options={{ 
                    scales: { 
                      y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#9ca3af' } },
                      x: { grid: { display: false }, ticks: { color: '#9ca3af' } }
                    },
                    plugins: { legend: { display: false } }
                  }}
                />
              </div>
            </div>

            {/* Difficulty Distribution */}
            <div className="glass-card chart-card">
              <h3><FiActivity /> {t('admin.difficulty_distribution') || 'Répartition par Difficulté'}</h3>
              <div className="chart-container">
                <PolarArea 
                  data={{
                    labels: advStats?.difficulty_distribution.map(d => d.difficulty) || [],
                    datasets: [{
                      data: advStats?.difficulty_distribution.map(d => d.count) || [],
                      backgroundColor: ['rgba(16, 185, 129, 0.5)', 'rgba(245, 158, 11, 0.5)', 'rgba(239, 68, 68, 0.5)'],
                      borderColor: '#111827',
                    }]
                  }}
                  options={{ 
                    scales: { r: { grid: { color: 'rgba(255,255,255,0.1)' }, ticks: { display: false } } },
                    plugins: { legend: { position: 'bottom', labels: { color: '#9ca3af' } } } 
                  }}
                />
              </div>
            </div>

            {/* Supervisor Workload */}
            <div className="glass-card chart-card">
              <h3><FiUsers /> {t('admin.supervisor_workload') || 'Charge de Travail Encadrants'}</h3>
              <div className="chart-container">
                <Bar 
                  data={{
                    labels: advStats?.supervisors_workload.map(s => `M. ${s.supervisor__last_name}`) || [],
                    datasets: [{
                      label: t('admin.projects') || 'Projets',
                      data: advStats?.supervisors_workload.map(s => s.count) || [],
                      backgroundColor: '#06b6d4',
                      borderRadius: 6,
                    }]
                  }}
                  options={{ 
                    indexAxis: 'y',
                    scales: { 
                      x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#9ca3af' } },
                      y: { grid: { display: false }, ticks: { color: '#9ca3af' } }
                    },
                    plugins: { legend: { display: false } }
                  }}
                />
              </div>
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
