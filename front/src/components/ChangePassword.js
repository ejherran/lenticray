// src/components/ChangePassword.js
import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';

function ChangePassword() {
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const navigate = useNavigate();

  const handleChangePassword = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${process.env.REACT_APP_API_URL}/users/change-password`,
        {
          old_password: oldPassword,
          new_password: newPassword,
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );
      alert(response.data.msg);
      navigate('/home');
    } catch (error) {
      console.error('Error changing password:', error);
      if (error.response && error.response.data && error.response.data.detail) {
        alert(`Error: ${error.response.data.detail}`);
      } else {
        alert('Failed to change password');
      }
    }
  };

  return (
    <div className="container d-flex justify-content-center align-items-center vh-100">
      <div className="card p-4 shadow-lg" style={{ maxWidth: '400px', width: '100%' }}>
        <form onSubmit={handleChangePassword}>
          <div className="mb-3">
            <label htmlFor="oldPassword" className="form-label">Old Password:</label>
            <input
              type="password"
              className="form-control"
              id="oldPassword"
              required
              value={oldPassword}
              onChange={(e) => setOldPassword(e.target.value)}
              placeholder="Enter your old password"
            />
          </div>
          <div className="mb-3">
            <label htmlFor="newPassword" className="form-label">New Password:</label>
            <input
              type="password"
              className="form-control"
              id="newPassword"
              required
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="Enter your new password"
            />
          </div>
          <button type="submit" className="btn btn-primary w-100">Change Password</button>
        </form>
      </div>
    </div>
  );
}

export default ChangePassword;
