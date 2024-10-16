// src/api/api.js
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'https://api.lenticray.ice-ing.co/api/v1';

const api = axios.create({
  baseURL: API_URL,
});

// Interceptor para agregar el token de autenticación en cada solicitud
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
