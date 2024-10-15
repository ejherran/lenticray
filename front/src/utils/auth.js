// src/utils/auth.js
export const isAuthenticated = () => {
  const token = localStorage.getItem('token');
  // Opcionalmente, puedes verificar si el token ha expirado
  return !!token;
};
