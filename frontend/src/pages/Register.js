import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { FiMail, FiLock, FiUser, FiBookOpen, FiCpu } from 'react-icons/fi';
import './Auth.css';

export default function Register() {
  const [formData, setFormData] = useState({
    email: '', username: '', password: '', password_confirm: '',
    first_name: '', last_name: '', university: '', field_of_study: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (formData.password !== formData.password_confirm) {
      setError('Les mots de passe ne correspondent pas.');
      return;
    }
    setLoading(true);
    try {
      await register(formData);
      navigate('/dashboard');
    } catch (err) {
      const data = err.response?.data;
      if (data) {
        const messages = Object.values(data).flat().join(' ');
        setError(messages);
      } else {
        setError("Erreur lors de l'inscription.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-bg-shapes">
        <div className="shape shape-1"></div>
        <div className="shape shape-2"></div>
        <div className="shape shape-3"></div>
      </div>

      <div className="auth-container auth-container-wide animate-fade-in">
        <div className="auth-header">
          <div className="auth-logo">
            <FiCpu />
            <span>Smart PFE</span>
          </div>
          <h1>Créer un compte 🚀</h1>
          <p>Rejoignez la plateforme et trouvez votre PFE idéal</p>
        </div>

        {error && <div className="auth-error">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Prénom</label>
              <div className="input-icon-wrapper">
                <FiUser className="input-icon" />
                <input type="text" className="form-input" name="first_name"
                  placeholder="Mohamed" value={formData.first_name}
                  onChange={handleChange} required />
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Nom</label>
              <div className="input-icon-wrapper">
                <FiUser className="input-icon" />
                <input type="text" className="form-input" name="last_name"
                  placeholder="Bouchoucha" value={formData.last_name}
                  onChange={handleChange} required />
              </div>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Nom d'utilisateur</label>
              <input type="text" className="form-input" name="username"
                placeholder="mohamed_b" value={formData.username}
                onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label className="form-label">Email</label>
              <div className="input-icon-wrapper">
                <FiMail className="input-icon" />
                <input type="email" className="form-input" name="email"
                  placeholder="votre@email.com" value={formData.email}
                  onChange={handleChange} required />
              </div>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Université</label>
              <div className="input-icon-wrapper">
                <FiBookOpen className="input-icon" />
                <input type="text" className="form-input" name="university"
                  placeholder="Université de Batna" value={formData.university}
                  onChange={handleChange} />
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Domaine d'études</label>
              <input type="text" className="form-input" name="field_of_study"
                placeholder="Génie Logiciel" value={formData.field_of_study}
                onChange={handleChange} />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Mot de passe</label>
              <div className="input-icon-wrapper">
                <FiLock className="input-icon" />
                <input type="password" className="form-input" name="password"
                  placeholder="••••••••" value={formData.password}
                  onChange={handleChange} required />
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Confirmer</label>
              <div className="input-icon-wrapper">
                <FiLock className="input-icon" />
                <input type="password" className="form-input" name="password_confirm"
                  placeholder="••••••••" value={formData.password_confirm}
                  onChange={handleChange} required />
              </div>
            </div>
          </div>

          <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
            {loading ? 'Inscription...' : "S'inscrire"}
          </button>
        </form>

        <p className="auth-switch">
          Déjà inscrit ? <Link to="/login">Se connecter</Link>
        </p>
      </div>
    </div>
  );
}
