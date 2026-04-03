import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { projectsAPI, favoritesAPI, conversationsAPI, recommendationsAPI } from '../services/api';
import { FiFolder, FiHeart, FiMessageSquare, FiTrendingUp, FiArrowRight, FiRefreshCw, FiStar } from 'react-icons/fi';
import { Link } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import './Dashboard.css';

export default function Dashboard() {
  const { user } = useAuth();
  const { t, i18n } = useTranslation();
  const [stats, setStats] = useState({ projects: 0, favorites: 0, conversations: 0 });
  const [recentProjects, setRecentProjects] = useState([]);
  const [recommendedProjects, setRecommendedProjects] = useState([]);
  const [loadingRecommendations, setLoadingRecommendations] = useState(false);

  useEffect(() => {
    fetchData();
    fetchRecommendations();
  }, [i18n.language]); // Refetch if language changes to get translated content

  const fetchData = async () => {
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
  };

  const fetchRecommendations = async () => {
    try {
      const { data } = await recommendationsAPI.list();
      setRecommendedProjects(data.results || data || []);
    } catch (err) {
      console.error('Fetch recommendations error:', err);
    }
  };

  const handleRefreshRecommendations = async () => {
    setLoadingRecommendations(true);
    try {
      const { data } = await recommendationsAPI.refresh();
      setRecommendedProjects(data);
      toast.success(t('dashboard.refresh_success') || 'Recommandations mises à jour !');
    } catch (err) {
      toast.error(t('dashboard.refresh_error') || 'Erreur lors de la mise à jour des recommandations.');
      console.error('Refresh recommendations error:', err);
    } finally {
      setLoadingRecommendations(false);
    }
  };

  const domainColors = {
    IA: '#7c3aed', Web: '#06b6d4', DevOps: '#f59e0b',
    Cybersecurity: '#ef4444', DataScience: '#10b981',
    Mobile: '#ec4899', IoT: '#8b5cf6', Cloud: '#3b82f6',
  };

  return (
    <div className="dashboard animate-fade-in">
      <div className="page-header">
        <h1>{t('dashboard.welcome', { name: user?.first_name || user?.username }) || `Bonjour, ${user?.first_name || user?.username} 👋`}</h1>
        <p>{t('dashboard.subtitle') || 'Bienvenue sur votre tableau de bord Smart PFE'}</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-4">
        <div className="glass-card stat-card">
          <div className="stat-icon purple"><FiFolder /></div>
          <div className="stat-info">
            <h3>{stats.projects}</h3>
            <p>{t('admin.projects')}</p>
          </div>
        </div>
        <div className="glass-card stat-card">
          <div className="stat-icon cyan"><FiHeart /></div>
          <div className="stat-info">
            <h3>{stats.favorites}</h3>
            <p>{t('common.favorites')}</p>
          </div>
        </div>
        <div className="glass-card stat-card">
          <div className="stat-icon green"><FiMessageSquare /></div>
          <div className="stat-info">
            <h3>{stats.conversations}</h3>
            <p>{t('common.conversations')}</p>
          </div>
        </div>
        <div className="glass-card stat-card">
          <div className="stat-icon orange"><FiTrendingUp /></div>
          <div className="stat-info">
            <h3>{recommendedProjects.length > 0 ? (t('dashboard.optimal') || 'Optimal') : '--'}</h3>
            <p>{t('dashboard.reco_status') || 'Statut Recommandation'}</p>
          </div>
        </div>
      </div>

      {/* Recommended Projects */}
      <div className="dashboard-section">
        <div className="section-header">
          <h2>
            <FiStar className="section-icon" style={{ color: 'var(--warning)' }} />
            {t('dashboard.recommended_for_you')}
          </h2>
          <button 
            className={`btn btn-ghost ${loadingRecommendations ? 'animate-spin' : ''}`}
            onClick={handleRefreshRecommendations}
            disabled={loadingRecommendations}
          >
            <FiRefreshCw /> {loadingRecommendations ? t('common.loading') : t('dashboard.refresh')}
          </button>
        </div>
        
        {recommendedProjects.length > 0 ? (
          <div className="grid grid-2">
            {recommendedProjects.map((reco) => (
              <div key={reco.id} className="glass-card project-card recommendation-card">
                <div className="project-card-header">
                  <span
                    className="project-domain-badge"
                    style={{ background: `${domainColors[reco.project?.domain] || '#7c3aed'}20`, color: domainColors[reco.project?.domain] || '#7c3aed' }}
                  >
                    {reco.project?.domain}
                  </span>
                  <span className="reco-score">
                    <FiTrendingUp /> {Math.round(reco.score * 100)}% Match
                  </span>
                </div>
                <h3>{reco.project?.title}</h3>
                <p className="reco-reason">{reco.reason}</p>
                <div className="project-tech">{reco.project?.technologies}</div>
                <Link to="/projects" className="btn btn-ghost btn-sm" style={{ marginTop: '1rem' }}>
                  {t('common.learn_more') || 'En savoir plus'} <FiArrowRight />
                </Link>
              </div>
            ))}
          </div>
        ) : (
          <div className="glass-card empty-state">
            <p>{t('dashboard.empty_recommendations') || 'Complétez votre profil pour obtenir des recommandations.'}</p>
            <Link to="/upload" className="btn btn-primary btn-sm" style={{ marginTop: '1rem' }}>
              {t('dashboard.add_skills') || 'Ajouter des compétences'}
            </Link>
          </div>
        )}
      </div>

      {/* Recent Projects */}
      {recentProjects.length > 0 && (
        <div className="dashboard-section">
          <div className="section-header">
            <h2>{t('dashboard.recent_projects') || 'Projets récents'}</h2>
            <Link to="/projects" className="btn btn-ghost">{t('common.view_all') || 'Voir tout'} <FiArrowRight /></Link>
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
