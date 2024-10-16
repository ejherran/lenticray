// src/components/Sidebar.js
import React from 'react';
import { NavLink } from 'react-router-dom';

function Sidebar() {
  const menuItems = [
    { path: '/', label: 'Home', exact: true },
    { path: '/projects', label: 'Projects' },
    { path: '/datasets', label: 'Datasets' },
    { path: '/studies', label: 'Studies' },
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
            Logout
          </button>
        </li>
      </ul>
    </div>
  );
}

export default Sidebar;
