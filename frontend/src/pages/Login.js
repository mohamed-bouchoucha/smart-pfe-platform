import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { FiMail, FiLock, FiCpu } from 'react-icons/fi';
import toast from 'react-hot-toast';
import './Auth.css';

export default function Login() {
  const { t } = useTranslation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const user = await login(email, password);
      toast.success(`${t('dashboard.welcome', { name: user.first_name || user.username })} !`);
      navigate(user.role === 'admin' ? '/admin' : '/dashboard');
    } catch (err) {
      const msg = err.response?.data?.detail || t('auth.login_error') || 'Email ou mot de passe incorrect.';
      setError(msg);
      toast.error(msg);
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

      <div className="auth-container animate-fade-in">
        <div className="auth-header">
          <div className="auth-logo">
            <FiCpu />
            <span>Smart PFE</span>
          </div>
          <h1>{t('auth.welcome_back')}</h1>
          <p>{t('auth.login_subtitle')}</p>
        </div>

        {error && <div className="auth-error">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label className="form-label">{t('auth.email')}</label>
            <div className="input-icon-wrapper">
              <FiMail className="input-icon" />
              <input
                type="email"
                className="form-input"
                placeholder={t('auth.email_placeholder')}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">{t('auth.password')}</label>
            <div className="input-icon-wrapper">
              <FiLock className="input-icon" />
              <input
                type="password"
                className="form-input"
                placeholder={t('auth.password_placeholder')}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
          </div>

          <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
            {loading ? t('auth.logging_in') : t('auth.login_button')}
          </button>
        </form>

        <p className="auth-switch">
          {t('auth.no_account')} <Link to="/register">{t('auth.register')}</Link>
        </p>
      </div>
    </div>
  );
}
