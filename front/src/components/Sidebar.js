// src/components/Sidebar.js
import React from 'react';
import { NavLink } from 'react-router-dom';

function Sidebar() {
  const menuItems = [
    { path: '/', label: 'Home', icon: 'bi-house-door', exact: true },
    { path: '/projects', label: 'Projects', icon: 'bi-briefcase' },
    { path: '/datasets', label: 'Datasets', icon: 'bi-file-earmark-spreadsheet' },
    { path: '/studies', label: 'Studies', icon: 'bi-journal' },
  ];

  return (
    <div className="sidebar bg-light">
      <ul className="list-unstyled m-0">
        {menuItems.map((item) => (
          <li key={item.path}>
            <NavLink
              to={item.path}
              className="text-decoration-none p-2 d-block"
              style={({ isActive }) => ({
                backgroundColor: isActive ? '#007bff' : '',
                color: isActive ? 'white' : '',
              })}
              end={item.exact || false}
            >
              <i className={`bi ${item.icon} me-2`}></i>
              {item.label}
            </NavLink>
          </li>
        ))}
        <li>
          <button
            className="btn btn-link text-decoration-none p-2 d-block"
            onClick={() => {
              window.location.href = '/change-password';
            }}
          >
            <i className="bi bi-lock me-2"></i>
            Change Password
          </button>
        </li>
        <li>
          <button
            className="btn btn-link text-decoration-none p-2 d-block"
            onClick={() => {
              localStorage.removeItem('token');
              window.location.href = '/login';
            }}
          >
            <i className="bi bi-box-arrow-right me-2"></i>
            Logout
          </button>
        </li>
      </ul>
    </div>
  );
}

export default Sidebar;
