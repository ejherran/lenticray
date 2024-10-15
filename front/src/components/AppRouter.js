// src/components/AppRouter.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './Login';
import Register from './Register';
import PrivateRoute from './PrivateRoute';
import Home from './Home';
import ProjectList from './ProjectList';
import ProjectCreate from './ProjectCreate';
import ProjectEdit from './ProjectEdit';

function AppRouter() {
  return (
    <Router>
      <Routes>
        {/* Rutas públicas */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Rutas protegidas */}
        <Route
          path="/"
          element={
            <PrivateRoute>
              <Home />
            </PrivateRoute>
          }
        />
        <Route
          path="/projects"
          element={
            <PrivateRoute>
              <ProjectList />
            </PrivateRoute>
          }
        />
        <Route
          path="/projects/create"
          element={
            <PrivateRoute>
              <ProjectCreate />
            </PrivateRoute>
          }
        />
        <Route
          path="/projects/edit/:id"
          element={
            <PrivateRoute>
              <ProjectEdit />
            </PrivateRoute>
          }
        />

        {/* Redirigir rutas desconocidas al home o login */}
        <Route
          path="*"
          element={
            <Navigate to={localStorage.getItem('token') ? '/' : '/login'} replace />
          }
        />
      </Routes>
    </Router>
  );
}

export default AppRouter;