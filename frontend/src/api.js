import axios from "axios";

// Create an axios instance with the base URL from your .env
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL + "/api",
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
