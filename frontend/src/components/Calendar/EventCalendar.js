import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { eventsAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { FiChevronLeft, FiChevronRight, FiPlus, FiX, FiCalendar, FiClock, FiFlag } from 'react-icons/fi';
import { motion, AnimatePresence } from 'framer-motion';
import './EventCalendar.css';

const EVENT_COLORS = {
  deadline: '#ef4444',
  interview: '#f59e0b',
  milestone: '#6366f1',
};

const EVENT_ICONS = {
  deadline: <FiFlag />,
  interview: <FiClock />,
  milestone: <FiCalendar />,
};

export default function EventCalendar() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [currentDate, setCurrentDate] = useState(new Date());
  const [events, setEvents] = useState([]);
  const [selectedDay, setSelectedDay] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [newEvent, setNewEvent] = useState({
    title: '', description: '', event_type: 'deadline', date: '', is_global: false,
  });

  const fetchEvents = async () => {
    try {
      const { data } = await eventsAPI.list();
      setEvents(data.results || data);
    } catch (err) {
      console.error('Fetch events error:', err);
    }
  };

  useEffect(() => { fetchEvents(); }, []);

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();
  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const today = new Date();

  const monthNames = [
    'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
    'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre',
  ];
  const dayNames = ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam'];

  const prevMonth = () => setCurrentDate(new Date(year, month - 1, 1));
  const nextMonth = () => setCurrentDate(new Date(year, month + 1, 1));

  const getEventsForDay = (day) => {
    return events.filter((e) => {
      const d = new Date(e.date);
      return d.getFullYear() === year && d.getMonth() === month && d.getDate() === day;
    });
  };

  const handleCreateEvent = async (e) => {
    e.preventDefault();
    try {
      await eventsAPI.create(newEvent);
      setShowModal(false);
      setNewEvent({ title: '', description: '', event_type: 'deadline', date: '', is_global: false });
      fetchEvents();
    } catch (err) {
      console.error('Create event error:', err);
    }
  };

  const handleDeleteEvent = async (id) => {
    try {
      await eventsAPI.delete(id);
      fetchEvents();
    } catch (err) {
      console.error('Delete event error:', err);
    }
  };

  const renderDays = () => {
    const cells = [];
    // Empty cells before first day
    for (let i = 0; i < firstDay; i++) {
      cells.push(<div key={`empty-${i}`} className="calendar-cell empty" />);
    }
    // Day cells
    for (let day = 1; day <= daysInMonth; day++) {
      const dayEvents = getEventsForDay(day);
      const isToday = today.getFullYear() === year && today.getMonth() === month && today.getDate() === day;
      const isSelected = selectedDay === day;

      cells.push(
        <div
          key={day}
          className={`calendar-cell ${isToday ? 'today' : ''} ${isSelected ? 'selected' : ''} ${dayEvents.length > 0 ? 'has-events' : ''}`}
          onClick={() => setSelectedDay(day === selectedDay ? null : day)}
        >
          <span className="day-number">{day}</span>
          {dayEvents.length > 0 && (
            <div className="event-dots">
              {dayEvents.slice(0, 3).map((ev, i) => (
                <span key={i} className="event-dot" style={{ background: EVENT_COLORS[ev.event_type] }} />
              ))}
            </div>
          )}
        </div>
      );
    }
    return cells;
  };

  const selectedDayEvents = selectedDay ? getEventsForDay(selectedDay) : [];

  return (
    <div className="event-calendar">
      <div className="calendar-header">
        <button className="btn-nav" onClick={prevMonth}><FiChevronLeft /></button>
        <h2>{monthNames[month]} {year}</h2>
        <button className="btn-nav" onClick={nextMonth}><FiChevronRight /></button>
        <button className="btn-add-event" onClick={() => setShowModal(true)}>
          <FiPlus /> {t('common.add_event') || 'Ajouter'}
        </button>
      </div>

      <div className="calendar-grid">
        {dayNames.map((d) => (
          <div key={d} className="calendar-cell day-header">{d}</div>
        ))}
        {renderDays()}
      </div>

      {/* Selected Day Detail Panel */}
      <AnimatePresence>
        {selectedDay && (
          <motion.div
            className="day-detail glass-card"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
          >
            <h3>{selectedDay} {monthNames[month]} {year}</h3>
            {selectedDayEvents.length === 0 ? (
              <p className="no-events">{t('common.no_events') || 'Aucun événement ce jour.'}</p>
            ) : (
              <div className="events-list">
                {selectedDayEvents.map((ev) => (
                  <div key={ev.id} className="event-item" style={{ borderLeft: `4px solid ${EVENT_COLORS[ev.event_type]}` }}>
                    <div className="event-item-header">
                      <span className="event-icon">{EVENT_ICONS[ev.event_type]}</span>
                      <span className="event-title">{ev.title}</span>
                      <button className="btn-delete-event" onClick={() => handleDeleteEvent(ev.id)}><FiX /></button>
                    </div>
                    {ev.description && <p className="event-desc">{ev.description}</p>}
                    {ev.project_title && <span className="event-project">{ev.project_title}</span>}
                    {ev.is_global && <span className="badge-global">Global</span>}
                  </div>
                ))}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Create Event Modal */}
      <AnimatePresence>
        {showModal && (
          <motion.div
            className="modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowModal(false)}
          >
            <motion.div
              className="modal-content glass-card"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <h3>{t('common.new_event') || 'Nouvel Événement'}</h3>
              <form onSubmit={handleCreateEvent}>
                <input
                  type="text"
                  placeholder={t('common.event_title') || 'Titre'}
                  value={newEvent.title}
                  onChange={(e) => setNewEvent({ ...newEvent, title: e.target.value })}
                  required
                />
                <textarea
                  placeholder={t('common.event_description') || 'Description (optionnel)'}
                  value={newEvent.description}
                  onChange={(e) => setNewEvent({ ...newEvent, description: e.target.value })}
                />
                <select
                  value={newEvent.event_type}
                  onChange={(e) => setNewEvent({ ...newEvent, event_type: e.target.value })}
                >
                  <option value="deadline">{t('common.deadline') || 'Date Limite'}</option>
                  <option value="interview">{t('common.interview') || 'Entretien'}</option>
                  <option value="milestone">{t('common.milestone') || 'Jalon'}</option>
                </select>
                <input
                  type="datetime-local"
                  value={newEvent.date}
                  onChange={(e) => setNewEvent({ ...newEvent, date: e.target.value })}
                  required
                />
                {user?.role === 'admin' && (
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={newEvent.is_global}
                      onChange={(e) => setNewEvent({ ...newEvent, is_global: e.target.checked })}
                    />
                    {t('common.broadcast_all') || 'Diffuser à tous les étudiants'}
                  </label>
                )}
                <div className="modal-actions">
                  <button type="button" className="btn-cancel" onClick={() => setShowModal(false)}>
                    {t('common.cancel') || 'Annuler'}
                  </button>
                  <button type="submit" className="btn-submit">
                    {t('common.create') || 'Créer'}
                  </button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
