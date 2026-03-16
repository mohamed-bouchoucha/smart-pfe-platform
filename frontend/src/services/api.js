import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 — try refreshing the token
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refresh = localStorage.getItem('refresh_token');
      if (refresh) {
        try {
          const { data } = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, { refresh });
          localStorage.setItem('access_token', data.access);
          originalRequest.headers.Authorization = `Bearer ${data.access}`;
          return api(originalRequest);
        } catch {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

// ===================== AUTH =====================
export const authAPI = {
  register: (data) => api.post('/auth/register/', data),
  login: (data) => api.post('/auth/login/', data),
  getProfile: () => api.get('/auth/me/'),
  updateProfile: (data) => api.patch('/auth/me/', data),
  getUsers: () => api.get('/auth/users/'),
};

// ===================== PROJECTS =====================
export const projectsAPI = {
  list: (params) => api.get('/projects/', { params }),
  get: (id) => api.get(`/projects/${id}/`),
  create: (data) => api.post('/projects/', data),
  update: (id, data) => api.patch(`/projects/${id}/`, data),
  delete: (id) => api.delete(`/projects/${id}/`),
  validate: (id, status) => api.patch(`/projects/${id}/validate/`, { status }),
  getSkills: () => api.get('/projects/skills/'),
};

// ===================== FAVORITES =====================
export const favoritesAPI = {
  list: () => api.get('/projects/favorites/'),
  add: (projectId) => api.post('/projects/favorites/', { project_id: projectId }),
  remove: (id) => api.delete(`/projects/favorites/${id}/`),
};

// ===================== CONVERSATIONS =====================
export const conversationsAPI = {
  list: () => api.get('/conversations/'),
  get: (id) => api.get(`/conversations/${id}/`),
  create: (data) => api.post('/conversations/', data || {}),
  delete: (id) => api.delete(`/conversations/${id}/`),
  sendMessage: (conversationId, content) =>
    api.post(`/conversations/${conversationId}/messages/`, { content }),
};

// ===================== DOCUMENTS =====================
export const documentsAPI = {
  list: () => api.get('/documents/'),
  upload: (file, docType) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('doc_type', docType);
    return api.post('/documents/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  delete: (id) => api.delete(`/documents/${id}/`),
};

// ===================== RECOMMENDATIONS =====================
export const recommendationsAPI = {
  list: () => api.get('/recommendations/'),
};

// ===================== NOTIFICATIONS =====================
export const notificationsAPI = {
  list: () => api.get('/notifications/'),
  markRead: (id) => api.patch(`/notifications/${id}/read/`),
};

// ===================== ADMIN =====================
export const adminAPI = {
  getStats: () => api.get('/admin/stats/'),
};

export default api;
