import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FiArrowRight, FiCheck, FiX } from 'react-icons/fi';
import './HomePage.css';

const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { 
    opacity: 1, 
    y: 0,
    transition: { duration: 0.6, ease: "easeOut" }
  }
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15
    }
  }
};

export default function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="homepage">
      {/* Navbar */}
      <nav className="hp-navbar">
        <div className="hp-logo">SmartPFE</div>
        <div className="hp-nav-links">
          <a href="#features">Fonctionnalités</a>
          <a href="#pricing">Tarifs</a>
          <a href="#how-it-works">Comment ça marche</a>
          <a href="#testimonials">Avis</a>
        </div>
        <button className="btn btn-primary" onClick={() => navigate('/register')}>
          Commencer gratuitement
        </button>
      </nav>

      {/* Hero Section */}
      <header className="hero section">
        <motion.div 
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={staggerContainer}
        >
          <motion.span className="hero-badge" variants={fadeUp}>
            ✨ Nouveau : Chatbot IA v2.0 disponible
          </motion.span>
          <motion.h1 variants={fadeUp}>
            Trouvez votre PFE idéal avec <em>l'Intelligence Artificielle</em>
          </motion.h1>
          <motion.p variants={fadeUp}>
            La plateforme n°1 pour les étudiants en génie logiciel. 
            Dialoguez avec notre IA, uploadez vos compétences et recevez des suggestions sur-mesure.
          </motion.p>
          <motion.div className="hero-ctas" variants={fadeUp}>
            <button className="btn btn-primary" onClick={() => navigate('/register')}>
              Démarrer l'expérience <FiArrowRight />
            </button>
            <button className="btn btn-secondary" onClick={() => navigate('/register')}>
              Voir la démo
            </button>
          </motion.div>

          <motion.div className="hero-stats" variants={fadeUp}>
            <div className="stat-item">
              <h3>2K+</h3>
              <p>Projets réels</p>
            </div>
            <div className="stat-item">
              <h3>94%</h3>
              <p>Taux de match</p>
            </div>
            <div className="stat-item">
              <h3>500+</h3>
              <p>Étudiants actifs</p>
            </div>
            <div className="stat-item">
              <h3>48h</h3>
              <p>Délai moyen</p>
            </div>
          </motion.div>
        </motion.div>
      </header>

      {/* Features Section */}
      <section id="features" className="section">
        <div className="section-header">
          <h2 className="section-title">Tout ce qu'il vous faut pour réussir</h2>
          <p className="section-subtitle">
            Des outils puissants conçus spécifiquement pour les futurs ingénieurs en quête d'excellence.
          </p>
        </div>
        <motion.div 
          className="features-grid"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={staggerContainer}
        >
          <FeatureCard 
            icon="🤖" 
            title="Chatbot IA Expert" 
            description="Un assistant intelligent qui comprend vos aspirations et vous guide vers les meilleurs sujets." 
          />
          <FeatureCard 
            icon="🎯" 
            title="Recommandations" 
            description="Algorithmes de matching basés sur vos technologies préférées et votre niveau d'études." 
          />
          <FeatureCard 
            icon="📄" 
            title="Upload Documents" 
            description="Analysez votre CV ou vos rapports pour extraire automatiquement vos points forts." 
          />
          <FeatureCard 
            icon="⭐" 
            title="Gestion Favoris" 
            description="Gardez une trace des projets qui vous inspirent et comparez-les facilement." 
          />
          <FeatureCard 
            icon="🔍" 
            title="Recherche Avancée" 
            description="Filtrez par domaine, technologies, durée ou entreprise pour une précision maximale." 
          />
          <FeatureCard 
            icon="📊" 
            title="Analytics" 
            description="Suivez l'évolution de vos candidatures et les tendances technologiques du marché." 
          />
        </motion.div>
      </section>

      {/* How it Works Section */}
      <section id="how-it-works" className="section">
        <h2 className="section-title">Comment ça marche ?</h2>
        <p className="section-subtitle">Trouvez votre stage en 4 étapes simples et rapides.</p>
        
        <motion.div 
          className="steps-container"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={staggerContainer}
        >
          <StepItem number="1" title="Créer profil" />
          <StepItem number="2" title="Dialoguer IA" />
          <StepItem number="3" title="Suggestions" />
          <StepItem number="4" title="Postuler" />
        </motion.div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="section">
        <h2 className="section-title">Des tarifs simples et transparents</h2>
        <p className="section-subtitle">Choisissez le plan qui correspond le mieux à vos ambitions.</p>
        
        <motion.div 
          className="pricing-grid"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={staggerContainer}
        >
          {/* Free Plan */}
          <motion.div className="pricing-card" variants={fadeUp}>
            <h3>Gratuit</h3>
            <div className="price-tag">0 DT <span>/vie</span></div>
            <ul className="pricing-features">
              <li><FiCheck className="check" /> Accès chatbot limité</li>
              <li><FiCheck className="check" /> 5 recommandations / jour</li>
              <li><FiCheck className="check" /> Recherche basique</li>
              <li><FiX className="cross" /> Upload documents</li>
              <li><FiX className="cross" /> Analytics avancés</li>
            </ul>
            <button className="btn btn-secondary btn-full" onClick={() => navigate('/register')}>S'inscrire</button>
          </motion.div>

          {/* Premium Plan */}
          <motion.div className="pricing-card popular" variants={fadeUp}>
            <div className="pop-badge">RECOMMANDÉ</div>
            <h3>Premium</h3>
            <div className="price-tag">29 DT <span>/mois</span></div>
            <ul className="pricing-features">
              <li><FiCheck className="check" /> Chatbot illimité</li>
              <li><FiCheck className="check" /> Suggestions prioritaires</li>
              <li><FiCheck className="check" /> Upload documents (PDF/Docx)</li>
              <li><FiCheck className="check" /> Recherche multicritères</li>
              <li><FiX className="cross" /> Support 1-on-1</li>
            </ul>
            <button className="btn btn-primary btn-full" onClick={() => navigate('/register')}>Prendre Premium</button>
          </motion.div>

          {/* Enterprise Plan */}
          <motion.div className="pricing-card" variants={fadeUp}>
            <h3>Entreprise</h3>
            <div className="price-tag">Sur devis</div>
            <ul className="pricing-features">
              <li><FiCheck className="check" /> Solution marque blanche</li>
              <li><FiCheck className="check" /> Dashboard université</li>
              <li><FiCheck className="check" /> Statistiques exportables</li>
              <li><FiCheck className="check" /> Support 24/7</li>
              <li><FiCheck className="check" /> API Access</li>
            </ul>
            <button className="btn btn-secondary btn-full" onClick={() => navigate('/register')}>Nous contacter</button>
          </motion.div>
        </motion.div>
      </section>

      {/* Testimonials */}
      <section id="testimonials" className="section">
        <h2 className="section-title">Ils nous font confiance</h2>
        <div className="testimonials-grid">
          <TestimonialCard 
            name="Sami Ben Ali" 
            school="ENSI" 
            text="Grâce au chatbot, j'ai trouvé un sujet en IA avant même le début de la période des stages." 
          />
          <TestimonialCard 
            name="Maya Rezgui" 
            school="ESPRIT" 
            text="L'interface est sublime et les suggestions sont incroyablement pertinentes par rapport à mon profil." 
          />
          <TestimonialCard 
            name="Ahmed Dridi" 
            school="INSAT" 
            text="Le gain de temps est énorme. Plus besoin de chercher sur 10 sites différents, tout est centralisé ici." 
          />
        </div>
      </section>

      {/* Final CTA */}
      <section className="final-cta section">
        <motion.div 
          initial={{ scale: 0.95, opacity: 0 }}
          whileInView={{ scale: 1, opacity: 1 }}
          viewport={{ once: true }}
        >
          <h2 className="section-title">Prêt à décrocher votre PFE de rêve ?</h2>
          <p className="section-subtitle">Rejoignez des centaines d'étudiants qui utilisent SmartPFE pour propulser leur carrière.</p>
          <div className="hero-ctas">
            <button className="btn btn-primary" onClick={() => navigate('/register')}>
              Créer mon compte maintenant
            </button>
          </div>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="hp-footer">
        <div className="hp-logo">SmartPFE</div>
        <div className="copyright">© 2026 SmartPFE. Tous droits réservés.</div>
        <div className="footer-links">
          <span>Confidentialité</span>
          <span>Conditions d'utilisation</span>
          <span>Contact</span>
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({ icon, title, description }) {
  return (
    <motion.div className="feature-card" variants={fadeUp}>
      <span className="feature-icon">{icon}</span>
      <h3>{title}</h3>
      <p>{description}</p>
    </motion.div>
  );
}

function StepItem({ number, title }) {
  return (
    <motion.div className="step-item" variants={fadeUp}>
      <div className="step-number">{number}</div>
      <h3>{title}</h3>
    </motion.div>
  );
}

function TestimonialCard({ name, school, text }) {
  const initials = name.split(' ').map(n => n[0]).join('');
  return (
    <motion.div className="testimonial-card" variants={fadeUp} whileHover={{ y: -5 }}>
      <div className="stars">★★★★★</div>
      <p>"{text}"</p>
      <div className="author">
        <div className="avatar">{initials}</div>
        <div className="author-info">
          <h4>{name}</h4>
          <span>{school}</span>
        </div>
      </div>
    </motion.div>
  );
}
