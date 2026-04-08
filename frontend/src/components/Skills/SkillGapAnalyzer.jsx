import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Radar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js';
import ReactMarkdown from 'react-markdown';
import { projectsAPI, skillsAPI } from '../../services/api';
import { FiTarget, FiBookOpen, FiZap } from 'react-icons/fi';
import './SkillGapAnalyzer.css';

// Register ChartJS modules
ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

export default function SkillGapAnalyzer({ projectId }) {
  const { t } = useTranslation();
  const [gapData, setGapData] = useState(null);
  const [recommendations, setRecommendations] = useState('');
  const [loading, setLoading] = useState(true);
  const [aiLoading, setAiLoading] = useState(false);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        const { data } = await projectsAPI.getSkillGap(projectId);
        setGapData(data);
        
        // Fetch AI recommendations if there are missing skills
        if (data.missing_skills?.length > 0) {
          setAiLoading(true);
          const res = await skillsAPI.recommendResources(data.missing_skills);
          setRecommendations(res.data.recommendations);
        } else {
          setRecommendations(t('common.no_missing_skills') || 'Félicitations ! Vous maîtrisez toutes les technologies requises.');
        }
      } catch (err) {
        console.error('Skill gap analysis error:', err);
      } finally {
        setLoading(false);
        setAiLoading(false);
      }
    }
    fetchData();
  }, [projectId, t]);

  if (loading) return <div className="loader"></div>;
  if (!gapData) return null;

  const chartData = {
    labels: gapData.labels,
    datasets: [
      {
        label: t('common.your_skills') || 'Vos compétences',
        data: gapData.user_scores,
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(59, 130, 246, 1)',
      },
      {
        label: t('common.required_skills') || 'Requis pour le projet',
        data: gapData.required_scores,
        backgroundColor: 'rgba(124, 58, 237, 0.1)',
        borderColor: 'rgba(124, 58, 237, 0.5)',
        borderWidth: 1,
        borderDash: [5, 5],
        pointBackgroundColor: 'rgba(124, 58, 237, 0.5)',
      },
    ],
  };

  const chartOptions = {
    scales: {
      r: {
        angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
        grid: { color: 'rgba(255, 255, 255, 0.1)' },
        pointLabels: { color: '#9ca3af', font: { size: 12 } },
        ticks: { display: false, stepSize: 1 },
        suggestedMin: 0,
        suggestedMax: 1,
      },
    },
    plugins: {
      legend: { labels: { color: '#f3f4f6' } },
    },
  };

  return (
    <div className="skill-gap-analyzer animate-fade-in">
      <div className="analyzer-header">
        <FiTarget className="header-icon" />
        <h3>{t('common.skill_matching') || 'Analyse de Correspondance'}</h3>
      </div>

      <div className="analyzer-grid">
        <div className="chart-container glass-card">
          <Radar data={chartData} options={chartOptions} />
        </div>

        <div className="resources-container glass-card">
          <h4>
            <FiBookOpen /> {t('common.learning_resources') || 'Ressources Recommandées'}
          </h4>
          {aiLoading ? (
            <div className="ai-loading">
              <FiZap className="zap-icon animate-pulse" />
              <span>{t('common.ai_thinking') || 'ARIA analyse les ressources...'}</span>
            </div>
          ) : (
            <div className="markdown-content">
              <ReactMarkdown>{recommendations}</ReactMarkdown>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
