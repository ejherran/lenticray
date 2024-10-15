// src/components/PrivateRoute.js
import React from 'react';
import { Navigate } from 'react-router-dom';
import { isAuthenticated } from '../utils/auth';
import AuthenticatedLayout from './AuthenticatedLayout';

function PrivateRoute({ children }) {
  return isAuthenticated() ? (
    <AuthenticatedLayout>{children}</AuthenticatedLayout>
  ) : (
    <Navigate to="/login" replace />
  );
}

export default PrivateRoute;
