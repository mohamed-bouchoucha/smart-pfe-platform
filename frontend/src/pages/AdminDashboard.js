import React, { useState, useEffect } from 'react';
import { adminAPI, authAPI, projectsAPI } from '../services/api';
import { FiUsers, FiFolder, FiMessageSquare, FiActivity, FiCheck, FiX, FiUserPlus, FiShield, FiUser } from 'react-icons/fi';
import { toast } from 'react-hot-toast';
import './Admin.css';

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [projects, setProjects] = useState([]);
  const [supervisors, setSupervisors] = useState([]);
  const [activeTab, setActiveTab] = useState('stats');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

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
      toast.error('Erreur lors du chargement des données.');
    } finally {
      setLoading(false);
    }
  };

  const handleProjectStatus = async (id, status) => {
    try {
      await projectsAPI.validate(id, status);
      toast.success(`Projet ${status === 'validated' ? 'validé' : 'rejeté'}`);
      fetchData();
    } catch (err) {
      toast.error('Erreur lors du changement de statut.');
    }
  };

  const handleAssignSupervisor = async (projectId, supervisorId) => {
    try {
      await projectsAPI.assign(projectId, supervisorId);
      toast.success('Encadrant assigné avec succès.');
      fetchData();
    } catch (err) {
      toast.error("Erreur lors de l'assignation.");
    }
  };

  const handleToggleUserActive = async (userId) => {
    try {
      await authAPI.toggleActive(userId);
      toast.success('Statut utilisateur mis à jour.');
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Erreur lors du changement de statut.');
    }
  };

  const handleChangeRole = async (userId, newRole) => {
    try {
      await authAPI.updateUser(userId, { role: newRole });
      toast.success(`Rôle mis à jour : ${newRole}`);
      fetchData();
    } catch (err) {
      toast.error('Erreur lors du changement de rôle.');
    }
  };

  return (
    <div className="admin-page animate-fade-in">
      <div className="page-header">
        <h1>Administration</h1>
        <p>Gérez la plateforme Smart PFE</p>
      </div>

      {/* Tabs */}
      <div className="admin-tabs">
        {[
          { key: 'stats', label: 'Statistiques', icon: <FiActivity /> },
          { key: 'users', label: 'Utilisateurs', icon: <FiUsers /> },
          { key: 'projects', label: 'Projets', icon: <FiFolder /> },
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

      {loading && <div className="loading-overlay">Chargement...</div>}

      {/* Stats Tab */}
      {activeTab === 'stats' && stats && (
        <div className="stats-content">
          <div className="grid grid-4">
            <div className="glass-card stat-card">
              <div className="stat-icon purple"><FiUsers /></div>
              <div className="stat-info">
                <h3>{stats.users?.total || 0}</h3>
                <p>Utilisateurs</p>
              </div>
            </div>
            <div className="glass-card stat-card">
              <div className="stat-icon cyan"><FiFolder /></div>
              <div className="stat-info">
                <h3>{stats.projects?.total || 0}</h3>
                <p>Projets</p>
              </div>
            </div>
            <div className="glass-card stat-card">
              <div className="stat-icon green"><FiMessageSquare /></div>
              <div className="stat-info">
                <h3>{stats.conversations?.total || 0}</h3>
                <p>Conversations</p>
              </div>
            </div>
            <div className="glass-card stat-card">
              <div className="stat-icon orange"><FiActivity /></div>
              <div className="stat-info">
                <h3>{stats.users?.active_today || 0}</h3>
                <p>Actifs aujourd'hui</p>
              </div>
            </div>
          </div>

          <div className="glass-card domain-stats-card">
            <h3>Projets par domaine</h3>
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
                  <th>Utilisateur</th>
                  <th>Rôle</th>
                  <th>Université</th>
                  <th>Statut</th>
                  <th>Actions</th>
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
                        <option value="student">Étudiant</option>
                        <option value="supervisor">Encadrant</option>
                        <option value="admin">Admin</option>
                      </select>
                    </td>
                    <td>{u.university || '—'}</td>
                    <td>
                      <span className={`badge badge-${u.is_active ? 'success' : 'danger'}`}>
                        {u.is_active ? 'Actif' : 'Désactivé'}
                      </span>
                    </td>
                    <td>
                      <button 
                        className={`btn btn-sm ${u.is_active ? 'btn-danger' : 'btn-success'}`}
                        onClick={() => handleToggleUserActive(u.id)}
                      >
                        {u.is_active ? 'Désactiver' : 'Activer'}
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
                  <th>Titre du Projet</th>
                  <th>Domaine / Difficulté</th>
                  <th>Encadrant</th>
                  <th>Statut</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {projects.map((p) => (
                  <tr key={p.id}>
                    <td>
                      <div className="project-cell">
                        <span className="project-title">{p.title}</span>
                        <span className="project-owner">Par {p.created_by_name}</span>
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
                        <option value="">Non assigné</option>
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
                          <button className="btn-icon success" title="Approuver" onClick={() => handleProjectStatus(p.id, 'approved')}>
                            <FiCheck />
                          </button>
                        )}
                        {p.status !== 'rejected' && (
                          <button className="btn-icon danger" title="Rejeter" onClick={() => handleProjectStatus(p.id, 'rejected')}>
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
