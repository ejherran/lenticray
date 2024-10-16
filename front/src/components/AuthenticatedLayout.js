// src/components/AuthenticatedLayout.js
import React from 'react';
import Sidebar from './Sidebar';
import './styles.css';

function AuthenticatedLayout({ children }) {
  return (
    <div className="d-flex">
      <Sidebar />
      <div className="content flex-grow-1 p-3">
        {children}
      </div>
    </div>
  );
}

export default AuthenticatedLayout;