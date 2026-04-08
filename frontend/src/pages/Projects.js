import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { projectsAPI, favoritesAPI } from '../services/api';
import { FiSearch, FiFilter, FiHeart, FiChevronDown, FiChevronUp } from 'react-icons/fi';
import StarRating from '../components/Rating/StarRating';
import ReviewSection from '../components/Reviews/ReviewSection';
import { authAPI } from '../services/api';
import './Projects.css';

export default function Projects() {
  const { t, i18n } = useTranslation();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [domainFilter, setDomainFilter] = useState('');
  const [expandedProject, setExpandedProject] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);

  const domains = ['', 'IA', 'Web', 'Mobile', 'DevOps', 'Cybersecurity', 'DataScience', 'IoT', 'Cloud'];
  const domainColors = {
    IA: '#7c3aed', Web: '#06b6d4', DevOps: '#f59e0b',
    Cybersecurity: '#ef4444', DataScience: '#10b981',
    Mobile: '#ec4899', IoT: '#8b5cf6', Cloud: '#3b82f6',
  };

  const fetchProjects = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (domainFilter) params.domain = domainFilter;
      if (search) params.search = search;
      const { data } = await projectsAPI.list(params);
      setProjects(data.results || data || []);
    } catch (err) {
      console.error('Fetch projects error:', err);
    } finally {
      setLoading(false);
    }
  }, [domainFilter, search, i18n.language]);

  useEffect(() => {
    fetchProjects();
    // Get current user to check if they can review
    authAPI.getProfile().then(res => setCurrentUser(res.data)).catch(() => {});
  }, [fetchProjects]);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchProjects();
  };

  const toggleFavorite = async (project) => {
    try {
      if (project.is_favorited) {
        const { data: favs } = await favoritesAPI.list();
        const fav = (favs.results || favs).find(f => f.project?.id === project.id);
        if (fav) await favoritesAPI.remove(fav.id);
      } else {
        await favoritesAPI.add(project.id);
      }
      fetchProjects();
    } catch (err) {
      console.error('Toggle favorite error:', err);
    }
  };

  return (
    <div className="projects-page animate-fade-in">
      <div className="page-header">
        <h1>{t('common.projects_catalog') || 'Catalogue de Projets'}</h1>
        <p>{t('common.projects_subtitle') || 'Explorez les projets de PFE et stages disponibles'}</p>
      </div>

      {/* Filters */}
      <div className="projects-filters glass-card">
        <form className="search-form" onSubmit={handleSearch}>
          <div className="search-wrapper">
            <FiSearch className="search-icon" />
            <input
              type="text"
              className="search-input"
              placeholder={t('common.search_placeholder') || 'Rechercher un projet...'}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </form>
        <div className="domain-filters">
          <FiFilter className="filter-icon" />
          {domains.map((d) => (
            <button
              key={d}
              className={`filter-chip ${domainFilter === d ? 'active' : ''}`}
              onClick={() => setDomainFilter(d)}
            >
              {d || t('common.all') || 'Tous'}
            </button>
          ))}
        </div>
      </div>

      {/* Project Grid */}
      <div className="grid grid-3">
        {projects.map((project) => (
          <div key={project.id} className="glass-card project-card-full">
            <div className="project-card-header">
              <span
                className="project-domain-badge"
                style={{ background: `${domainColors[project.domain] || '#7c3aed'}20`, color: domainColors[project.domain] || '#7c3aed' }}
              >
                {project.domain}
              </span>
              <button
                className={`favorite-btn ${project.is_favorited ? 'favorited' : ''}`}
                onClick={() => toggleFavorite(project)}
              >
                <FiHeart />
              </button>
            </div>
            <div className="project-rating-summary">
              <StarRating rating={project.average_rating} readOnly />
              <span className="review-count">({project.review_count})</span>
            </div>
            <h3>{project.title}</h3>
            <p className="project-desc">{project.description?.slice(0, 150)}...</p>
            <div className="project-meta">
              <span className={`badge badge-${project.difficulty === 'beginner' ? 'success' : project.difficulty === 'intermediate' ? 'warning' : 'danger'}`}>
                {t(`common.difficulty_${project.difficulty}`) || project.difficulty}
              </span>
              <span className="badge badge-info">{project.duration}</span>
            </div>
            <div className="project-tech">{project.technologies}</div>
            <button 
              className="btn-details"
              onClick={() => setExpandedProject(expandedProject === project.id ? null : project.id)}
            >
              {expandedProject === project.id ? (
                <><FiChevronUp /> {t('common.hide_reviews') || 'Masquer les avis'}</>
              ) : (
                <><FiChevronDown /> {t('common.view_reviews') || 'Voir les avis'}</>
              )}
            </button>

            {expandedProject === project.id && (
              <ReviewSection 
                projectId={project.id} 
                canReview={
                  currentUser?.role === 'student' && 
                  project.status === 'completed' && 
                  project.assigned_to === currentUser?.id
                }
                onReviewAdded={fetchProjects}
              />
            )}
          </div>
        ))}
      </div>

      {!loading && projects.length === 0 && (
        <div className="empty-state">
          <p>{t('common.no_projects_found') || "Aucun projet trouvé. Essayez d'autres filtres."}</p>
        </div>
      )}
    </div>
  );
}
