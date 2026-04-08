import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { reviewsAPI } from '../../services/api';
import StarRating from '../Rating/StarRating';
import { FiMessageSquare, FiSend } from 'react-icons/fi';
import './ReviewSection.css';

export default function ReviewSection({ projectId, canReview, onReviewAdded }) {
  const { t } = useTranslation();
  const [reviews, setReviews] = useState([]);
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchReviews = async () => {
    try {
      const { data } = await reviewsAPI.list(projectId);
      setReviews(data.results || data);
    } catch (err) {
      console.error('Fetch reviews error:', err);
    }
  };

  useEffect(() => {
    fetchReviews();
  }, [projectId]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await reviewsAPI.create({
        project: projectId,
        rating,
        comment,
      });
      setComment('');
      setRating(5);
      fetchReviews();
      if (onReviewAdded) onReviewAdded();
    } catch (err) {
      setError(err.response?.data?.detail || t('common.error_review') || 'Erreur lors de l\'envoi de l\'avis.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="review-section">
      <h3>
        <FiMessageSquare /> {t('common.reviews') || 'Avis'} ({reviews.length})
      </h3>

      {canReview && (
        <form className="review-form glass-card" onSubmit={handleSubmit}>
          <div className="form-group">
            <label>{t('common.rate_project') || 'Noter le projet'}</label>
            <StarRating rating={rating} setRating={setRating} />
          </div>
          <div className="form-group">
            <textarea
              placeholder={t('common.review_placeholder') || 'Partagez votre expérience sur ce projet...'}
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              required
            />
          </div>
          {error && <p className="error-text">{error}</p>}
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? <div className="loader small" /> : <><FiSend /> {t('common.submit') || 'Publier'}</>}
          </button>
        </form>
      )}

      <div className="review-list">
        {reviews.length === 0 ? (
          <p className="empty-state">{t('common.no_reviews') || 'Aucun avis pour le moment.'}</p>
        ) : (
          reviews.map((review) => (
            <div key={review.id} className="review-item glass-card">
              <div className="review-header">
                <span className="user-name">{review.user_name}</span>
                <span className="review-date">{new Date(review.created_at).toLocaleDateString()}</span>
              </div>
              <StarRating rating={review.rating} readOnly />
              <p className="review-comment">{review.comment}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
