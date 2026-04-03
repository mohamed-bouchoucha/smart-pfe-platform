import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { documentsAPI } from '../services/api';
import { FiUploadCloud, FiFile, FiTrash2, FiCheck } from 'react-icons/fi';
import './Upload.css';

export default function Upload() {
  const { t, i18n } = useTranslation();
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [docType, setDocType] = useState('cv');
  const fileInputRef = useRef(null);

  useEffect(() => {
    fetchDocuments();
  }, [i18n.language]);

  const fetchDocuments = async () => {
    try {
      const { data } = await documentsAPI.list();
      setDocuments(data.results || data || []);
    } catch (err) {
      console.error('Fetch documents error:', err);
    }
  };

  const handleUpload = async (files) => {
    if (!files || files.length === 0) return;
    setUploading(true);
    try {
      for (const file of files) {
        await documentsAPI.upload(file, docType);
      }
      fetchDocuments();
    } catch (err) {
      console.error('Upload error:', err);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await documentsAPI.delete(id);
      setDocuments(documents.filter((d) => d.id !== id));
    } catch (err) {
      console.error('Delete error:', err);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === 'dragenter' || e.type === 'dragover');
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    handleUpload(e.dataTransfer.files);
  };

  const docTypeLabels = { 
    cv: t('upload.cv') || 'CV', 
    cahier_charges: t('upload.cahier_charges') || 'Cahier des charges', 
    report: t('upload.report') || 'Rapport', 
    other: t('upload.other') || 'Autre' 
  };

  return (
    <div className="upload-page animate-fade-in">
      <div className="page-header">
        <h1>{t('upload.title') || 'Mes Documents'}</h1>
        <p>{t('upload.subtitle') || 'Uploadez vos CV et documents pour une analyse IA personnalisée'}</p>
      </div>

      {/* Upload Zone */}
      <div className="glass-card upload-section">
        <div className="upload-controls">
          <label className="form-label">{t('upload.doc_type') || 'Type de document'}</label>
          <select className="form-select" value={docType} onChange={(e) => setDocType(e.target.value)}>
            {Object.entries(docTypeLabels).map(([val, label]) => (
              <option key={val} value={val}>{label}</option>
            ))}
          </select>
        </div>

        <div
          className={`dropzone ${dragActive ? 'active' : ''}`}
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <FiUploadCloud className="dropzone-icon" />
          <p>
            <strong>{t('upload.dropzone_text') || 'Glissez vos fichiers ici'}</strong> 
            {t('upload.dropzone_click') || ' ou cliquez pour parcourir'}
          </p>
          <span>PDF, DOCX, TXT — Max 10 MB</span>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            className="hidden-input"
            onChange={(e) => handleUpload(e.target.files)}
            accept=".pdf,.doc,.docx,.txt"
          />
        </div>

        {uploading && <p className="upload-status">⏳ {t('upload.uploading') || 'Upload en cours...'}</p>}
      </div>

      {/* Document List */}
      {documents.length > 0 && (
        <div className="glass-card">
          <h3 style={{ marginBottom: 'var(--space-md)' }}>{t('upload.uploaded_docs') || 'Documents uploadés'}</h3>
          <div className="document-list">
            {documents.map((doc) => (
              <div key={doc.id} className="document-item">
                <FiFile className="doc-icon" />
                <div className="doc-info">
                  <span className="doc-name">{doc.filename}</span>
                  <span className="doc-meta">
                    {docTypeLabels[doc.doc_type] || doc.doc_type} · {(doc.file_size / 1024).toFixed(0)} KB
                  </span>
                </div>
                <div className="doc-status">
                  {doc.is_analyzed && (
                    <span className="badge badge-success">
                      <FiCheck /> {t('upload.analyzed') || 'Analysé'}
                    </span>
                  )}
                </div>
                <button className="btn btn-ghost" onClick={() => handleDelete(doc.id)}>
                  <FiTrash2 />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
