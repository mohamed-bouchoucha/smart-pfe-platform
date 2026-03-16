import React, { useState, useEffect } from 'react';
import { favoritesAPI } from '../../services/api';
import { FiHeart, FiTrash2 } from 'react-icons/fi';

export default function Favorites() {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchFavorites();
  }, []);

  const fetchFavorites = async () => {
    try {
      const { data } = await favoritesAPI.list();
      setFavorites(data.results || data || []);
    } catch (err) {
      console.error('Fetch favorites error:', err);
    } finally {
      setLoading(false);
    }
  };

  const removeFavorite = async (id) => {
    try {
      await favoritesAPI.remove(id);
      setFavorites(favorites.filter((f) => f.id !== id));
    } catch (err) {
      console.error('Remove favorite error:', err);
    }
  };

  const domainColors = {
    IA: '#7c3aed', Web: '#06b6d4', DevOps: '#f59e0b',
    Cybersecurity: '#ef4444', DataScience: '#10b981',
    Mobile: '#ec4899', IoT: '#8b5cf6', Cloud: '#3b82f6',
  };

  return (
    <div className="favorites-page animate-fade-in">
      <div className="page-header">
        <h1>Mes Favoris</h1>
        <p>Vos projets de PFE sauvegardés</p>
      </div>

      {favorites.length === 0 && !loading ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '3rem' }}>
          <FiHeart style={{ fontSize: '3rem', color: 'var(--text-muted)', marginBottom: '1rem' }} />
          <p style={{ color: 'var(--text-secondary)' }}>Aucun projet favori pour le moment.</p>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            Explorez le catalogue et sauvegardez vos projets préférés !
          </p>
        </div>
      ) : (
        <div className="grid grid-2">
          {favorites.map((fav) => (
            <div key={fav.id} className="glass-card project-card" style={{ position: 'relative' }}>
              <div className="project-card-header">
                <span
                  className="project-domain-badge"
                  style={{
                    background: `${domainColors[fav.project?.domain] || '#7c3aed'}20`,
                    color: domainColors[fav.project?.domain] || '#7c3aed',
                  }}
                >
                  {fav.project?.domain}
                </span>
                <span className={`badge badge-${
                  fav.project?.difficulty === 'beginner' ? 'success'
                  : fav.project?.difficulty === 'intermediate' ? 'warning' : 'danger'
                }`}>
                  {fav.project?.difficulty}
                </span>
              </div>
              <h3>{fav.project?.title}</h3>
              <p className="project-desc">{fav.project?.description?.slice(0, 150)}...</p>
              <div className="project-tech">{fav.project?.technologies}</div>
              <button
                className="btn btn-ghost"
                style={{ position: 'absolute', top: '1rem', right: '1rem', color: 'var(--danger)' }}
                onClick={() => removeFavorite(fav.id)}
              >
                <FiTrash2 />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
