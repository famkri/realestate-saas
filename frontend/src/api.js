import axios from "axios";

// Use the base URL directly from your .env
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
