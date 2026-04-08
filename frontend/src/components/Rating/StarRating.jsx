import React from 'react';
import { FiStar } from 'react-icons/fi';
import './StarRating.css';

export default function StarRating({ rating, setRating, readOnly = false }) {
  const [hover, setHover] = React.useState(0);

  return (
    <div className="star-rating">
      {[1, 2, 3, 4, 5].map((star) => (
        <FiStar
          key={star}
          className={`star-icon ${star <= (hover || rating) ? 'filled' : ''} ${readOnly ? 'read-only' : ''}`}
          onMouseEnter={() => !readOnly && setHover(star)}
          onMouseLeave={() => !readOnly && setHover(0)}
          onClick={() => !readOnly && setRating(star)}
        />
      ))}
    </div>
  );
}
