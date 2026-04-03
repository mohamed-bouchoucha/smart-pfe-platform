import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { FiMail, FiLock, FiUser, FiBookOpen, FiCpu } from 'react-icons/fi';
import toast from 'react-hot-toast';
import './Auth.css';

export default function Register() {
  const { t } = useTranslation();
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
      setError(t('auth.password_mismatch') || 'Les mots de passe ne correspondent pas.');
      return;
    }
    setLoading(true);
    try {
      await register(formData);
      toast.success(t('auth.register_success') || 'Compte créé avec succès !');
      navigate('/dashboard');
    } catch (err) {
      const data = err.response?.data;
      const msg = data ? Object.values(data).flat().join(' ') : (t('auth.register_error') || "Erreur lors de l'inscription.");
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

      <div className="auth-container auth-container-wide animate-fade-in">
        <div className="auth-header">
          <div className="auth-logo">
            <FiCpu />
            <span>Smart PFE</span>
          </div>
          <h1>{t('auth.register_title')}</h1>
          <p>{t('auth.register_subtitle')}</p>
        </div>

        {error && <div className="auth-error">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">{t('auth.first_name')}</label>
              <div className="input-icon-wrapper">
                <FiUser className="input-icon" />
                <input type="text" className="form-input" name="first_name"
                  placeholder={t('auth.first_name_placeholder')} value={formData.first_name}
                  onChange={handleChange} required />
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">{t('auth.last_name')}</label>
              <div className="input-icon-wrapper">
                <FiUser className="input-icon" />
                <input type="text" className="form-input" name="last_name"
                  placeholder={t('auth.last_name_placeholder')} value={formData.last_name}
                  onChange={handleChange} required />
              </div>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">{t('auth.username') || "Nom d'utilisateur"}</label>
              <input type="text" className="form-input" name="username"
                placeholder={t('auth.username_placeholder')} value={formData.username}
                onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label className="form-label">{t('auth.email')}</label>
              <div className="input-icon-wrapper">
                <FiMail className="input-icon" />
                <input type="email" className="form-input" name="email"
                  placeholder={t('auth.email_placeholder')} value={formData.email}
                  onChange={handleChange} required />
              </div>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">{t('auth.university')}</label>
              <div className="input-icon-wrapper">
                <FiBookOpen className="input-icon" />
                <input type="text" className="form-input" name="university"
                  placeholder={t('auth.university_placeholder')} value={formData.university}
                  onChange={handleChange} />
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">{t('auth.field_of_study')}</label>
              <input type="text" className="form-input" name="field_of_study"
                placeholder={t('auth.field_placeholder')} value={formData.field_of_study}
                onChange={handleChange} />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">{t('auth.password')}</label>
              <div className="input-icon-wrapper">
                <FiLock className="input-icon" />
                <input type="password" className="form-input" name="password"
                  placeholder={t('auth.password_placeholder')} value={formData.password}
                  onChange={handleChange} required />
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">{t('auth.confirm_password') || 'Confirmer'}</label>
              <div className="input-icon-wrapper">
                <FiLock className="input-icon" />
                <input type="password" className="form-input" name="password_confirm"
                  placeholder={t('auth.password_placeholder')} value={formData.password_confirm}
                  onChange={handleChange} required />
              </div>
            </div>
          </div>

          <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
            {loading ? t('auth.registering') : t('auth.register_button')}
          </button>
        </form>

        <p className="auth-switch">
          {t('auth.has_account')} <Link to="/login">{t('auth.login')}</Link>
        </p>
      </div>
    </div>
  );
}
