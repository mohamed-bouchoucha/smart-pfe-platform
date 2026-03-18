import React, { useState, useEffect } from 'react';
import { adminAPI, authAPI, projectsAPI } from '../services/api';
import { FiUsers, FiFolder, FiMessageSquare, FiActivity, FiCheck, FiX } from 'react-icons/fi';
import './Admin.css';

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [projects, setProjects] = useState([]);
  const [activeTab, setActiveTab] = useState('stats');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [statsRes, usersRes, projectsRes] = await Promise.allSettled([
        adminAPI.getStats(),
        authAPI.getUsers(),
        projectsAPI.list(),
      ]);
      if (statsRes.status === 'fulfilled') setStats(statsRes.value.data);
      if (usersRes.status === 'fulfilled') setUsers(usersRes.value.data.results || usersRes.value.data || []);
      if (projectsRes.status === 'fulfilled') setProjects(projectsRes.value.data.results || projectsRes.value.data || []);
    } catch (err) {
      console.error('Admin fetch error:', err);
    }
  };

  const handleProjectStatus = async (id, status) => {
    try {
      await projectsAPI.validate(id, status);
      fetchData();
    } catch (err) {
      console.error('Validate error:', err);
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
        {['stats', 'users', 'projects'].map((tab) => (
          <button
            key={tab}
            className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab === 'stats' && <><FiActivity /> Statistiques</>}
            {tab === 'users' && <><FiUsers /> Utilisateurs</>}
            {tab === 'projects' && <><FiFolder /> Projets</>}
          </button>
        ))}
      </div>

      {/* Stats Tab */}
      {activeTab === 'stats' && stats && (
        <div>
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

          {/* Domain Stats */}
          <div className="glass-card" style={{ marginTop: 'var(--space-xl)' }}>
            <h3 style={{ marginBottom: 'var(--space-md)' }}>Projets par domaine</h3>
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
        <div className="glass-card">
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Nom</th>
                  <th>Email</th>
                  <th>Rôle</th>
                  <th>Université</th>
                  <th>Inscrit le</th>
                  <th>Statut</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id}>
                    <td>{u.first_name} {u.last_name}</td>
                    <td>{u.email}</td>
                    <td><span className={`badge badge-${u.role === 'admin' ? 'primary' : 'info'}`}>{u.role}</span></td>
                    <td>{u.university || '—'}</td>
                    <td>{new Date(u.date_joined).toLocaleDateString('fr-FR')}</td>
                    <td><span className={`badge badge-${u.is_active ? 'success' : 'danger'}`}>{u.is_active ? 'Actif' : 'Inactif'}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Projects Tab */}
      {activeTab === 'projects' && (
        <div className="glass-card">
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Titre</th>
                  <th>Domaine</th>
                  <th>Difficulté</th>
                  <th>Statut</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {projects.map((p) => (
                  <tr key={p.id}>
                    <td>{p.title}</td>
                    <td><span className="badge badge-info">{p.domain}</span></td>
                    <td><span className={`badge badge-${p.difficulty === 'beginner' ? 'success' : p.difficulty === 'intermediate' ? 'warning' : 'danger'}`}>{p.difficulty}</span></td>
                    <td><span className={`badge badge-${p.status === 'validated' ? 'success' : p.status === 'rejected' ? 'danger' : 'warning'}`}>{p.status}</span></td>
                    <td>
                      <div className="action-btns">
                        {p.status !== 'validated' && (
                          <button className="btn btn-ghost" title="Valider" onClick={() => handleProjectStatus(p.id, 'validated')}>
                            <FiCheck style={{ color: 'var(--success)' }} />
                          </button>
                        )}
                        {p.status !== 'rejected' && (
                          <button className="btn btn-ghost" title="Rejeter" onClick={() => handleProjectStatus(p.id, 'rejected')}>
                            <FiX style={{ color: 'var(--danger)' }} />
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
