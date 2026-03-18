import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { projectsAPI, favoritesAPI, conversationsAPI } from '../services/api';
import { FiFolder, FiHeart, FiMessageSquare, FiTrendingUp, FiArrowRight } from 'react-icons/fi';
import { Link } from 'react-router-dom';
import './Dashboard.css';

export default function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState({ projects: 0, favorites: 0, conversations: 0 });
  const [recentProjects, setRecentProjects] = useState([]);

  useEffect(() => {
    async function fetchData() {
      try {
        const [projectsRes, favRes, convRes] = await Promise.allSettled([
          projectsAPI.list({ page_size: 4 }),
          favoritesAPI.list(),
          conversationsAPI.list(),
        ]);

        const projects = projectsRes.status === 'fulfilled' ? projectsRes.value.data : { results: [], count: 0 };
        const favs = favRes.status === 'fulfilled' ? favRes.value.data : { results: [], count: 0 };
        const convs = convRes.status === 'fulfilled' ? convRes.value.data : { results: [], count: 0 };

        setStats({
          projects: projects.count || projects.results?.length || 0,
          favorites: favs.count || favs.results?.length || 0,
          conversations: convs.count || convs.results?.length || 0,
        });
        setRecentProjects(projects.results?.slice(0, 4) || []);
      } catch (err) {
        console.error('Dashboard fetch error:', err);
      }
    }
    fetchData();
  }, []);

  const domainColors = {
    IA: '#7c3aed', Web: '#06b6d4', DevOps: '#f59e0b',
    Cybersecurity: '#ef4444', DataScience: '#10b981',
    Mobile: '#ec4899', IoT: '#8b5cf6', Cloud: '#3b82f6',
  };

  return (
    <div className="dashboard animate-fade-in">
      <div className="page-header">
        <h1>Bonjour, {user?.first_name || user?.username} 👋</h1>
        <p>Bienvenue sur votre tableau de bord Smart PFE</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-4">
        <div className="glass-card stat-card">
          <div className="stat-icon purple"><FiFolder /></div>
          <div className="stat-info">
            <h3>{stats.projects}</h3>
            <p>Projets disponibles</p>
          </div>
        </div>
        <div className="glass-card stat-card">
          <div className="stat-icon cyan"><FiHeart /></div>
          <div className="stat-info">
            <h3>{stats.favorites}</h3>
            <p>Projets favoris</p>
          </div>
        </div>
        <div className="glass-card stat-card">
          <div className="stat-icon green"><FiMessageSquare /></div>
          <div className="stat-info">
            <h3>{stats.conversations}</h3>
            <p>Conversations IA</p>
          </div>
        </div>
        <div className="glass-card stat-card">
          <div className="stat-icon orange"><FiTrendingUp /></div>
          <div className="stat-info">
            <h3>85%</h3>
            <p>Pertinence IA</p>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="dashboard-actions">
        <h2>Actions rapides</h2>
        <div className="grid grid-3">
          <Link to="/chatbot" className="glass-card action-card">
            <FiMessageSquare className="action-icon" />
            <h3>Discuter avec l'IA</h3>
            <p>Trouvez votre PFE idéal</p>
            <FiArrowRight className="action-arrow" />
          </Link>
          <Link to="/projects" className="glass-card action-card">
            <FiFolder className="action-icon" />
            <h3>Explorer les projets</h3>
            <p>Parcourir le catalogue</p>
            <FiArrowRight className="action-arrow" />
          </Link>
          <Link to="/upload" className="glass-card action-card">
            <FiTrendingUp className="action-icon" />
            <h3>Uploader un CV</h3>
            <p>Analyse IA de votre profil</p>
            <FiArrowRight className="action-arrow" />
          </Link>
        </div>
      </div>

      {/* Recent Projects */}
      {recentProjects.length > 0 && (
        <div className="dashboard-section">
          <div className="section-header">
            <h2>Projets récents</h2>
            <Link to="/projects" className="btn btn-ghost">Voir tout <FiArrowRight /></Link>
          </div>
          <div className="grid grid-2">
            {recentProjects.map((project) => (
              <div key={project.id} className="glass-card project-card">
                <div className="project-card-header">
                  <span
                    className="project-domain-badge"
                    style={{ background: `${domainColors[project.domain] || '#7c3aed'}20`, color: domainColors[project.domain] || '#7c3aed' }}
                  >
                    {project.domain}
                  </span>
                  <span className={`badge badge-${project.difficulty === 'beginner' ? 'success' : project.difficulty === 'intermediate' ? 'warning' : 'danger'}`}>
                    {project.difficulty}
                  </span>
                </div>
                <h3>{project.title}</h3>
                <p className="project-desc">{project.description?.slice(0, 120)}...</p>
                <div className="project-tech">{project.technologies}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
