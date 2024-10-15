// src/components/ProjectCreate.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/api';

function ProjectCreate() {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [latitude, setLatitude] = useState('');
  const [longitude, setLongitude] = useState('');
  const [area, setArea] = useState('');
  const [depth, setDepth] = useState('');
  const [volume, setVolume] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/projects/', {
        name,
        description: description || null,
        latitude: latitude !== '' ? parseFloat(latitude) : null,
        longitude: longitude !== '' ? parseFloat(longitude) : null,
        area: area !== '' ? parseFloat(area) : null,
        depth: depth !== '' ? parseFloat(depth) : null,
        volume: volume !== '' ? parseFloat(volume) : null,
      });
      alert('Project created successfully');
      navigate('/projects');
    } catch (error) {
      console.error('Error creating project:', error);
      alert('Failed to create project');
    }
  };

  return (
    <div>
      <h2>Create New Project</h2>
      <form onSubmit={handleSubmit}>
        {/* Nombre */}
        <div className="mb-3">
          <label>Name:</label>
          <input
            type="text"
            className="form-control"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </div>
        {/* Descripción */}
        <div className="mb-3">
          <label>Description:</label>
          <textarea
            className="form-control"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          ></textarea>
        </div>
        {/* Latitud */}
        <div className="mb-3">
          <label>Latitude:</label>
          <input
            type="number"
            step="any"
            className="form-control"
            value={latitude}
            onChange={(e) => setLatitude(e.target.value)}
          />
        </div>
        {/* Longitud */}
        <div className="mb-3">
          <label>Longitude:</label>
          <input
            type="number"
            step="any"
            className="form-control"
            value={longitude}
            onChange={(e) => setLongitude(e.target.value)}
          />
        </div>
        {/* Superficie */}
        <div className="mb-3">
          <label>Area:</label>
          <input
            type="number"
            step="any"
            className="form-control"
            value={area}
            onChange={(e) => setArea(e.target.value)}
          />
        </div>
        {/* Profundidad */}
        <div className="mb-3">
          <label>Depth:</label>
          <input
            type="number"
            step="any"
            className="form-control"
            value={depth}
            onChange={(e) => setDepth(e.target.value)}
          />
        </div>
        {/* Volumen */}
        <div className="mb-3">
          <label>Volume:</label>
          <input
            type="number"
            step="any"
            className="form-control"
            value={volume}
            onChange={(e) => setVolume(e.target.value)}
          />
        </div>
        <button type="submit" className="btn btn-primary">
          Create Project
        </button>
      </form>
    </div>
  );
}

export default ProjectCreate;
