// src/components/ProjectEdit.js
import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import api from '../api/api';

function ProjectEdit() {
  const [project, setProject] = useState(null);
  const { id } = useParams();
  const navigate = useNavigate();

  const fetchProject = async () => {
    try {
      const response = await api.get(`/projects/${id}`);
      setProject(response.data);
    } catch (error) {
      console.error('Error fetching project:', error);
      alert('Failed to fetch project');
    }
  };

  useEffect(() => {
    fetchProject();
  }, [id]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.put(`/projects/${id}`, {
        name: project.name,
        description: project.description || null,
        latitude: project.latitude !== '' ? parseFloat(project.latitude) : null,
        longitude: project.longitude !== '' ? parseFloat(project.longitude) : null,
        area: project.area !== '' ? parseFloat(project.area) : null,
        depth: project.depth !== '' ? parseFloat(project.depth) : null,
        volume: project.volume !== '' ? parseFloat(project.volume) : null,
      });
      alert('Project updated successfully');
      navigate('/projects');
    } catch (error) {
      console.error('Error updating project:', error);
      alert('Failed to update project');
    }
  };

  if (!project) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h2>Edit Project</h2>
      <form onSubmit={handleSubmit}>
        {/* Nombre */}
        <div className="mb-3">
          <label>Name:</label>
          <input
            type="text"
            className="form-control"
            required
            value={project.name}
            onChange={(e) => setProject({ ...project, name: e.target.value })}
          />
        </div>
        {/* Descripción */}
        <div className="mb-3">
          <label>Description:</label>
          <textarea
            className="form-control"
            value={project.description || ''}
            onChange={(e) => setProject({ ...project, description: e.target.value })}
          ></textarea>
        </div>
        {/* Latitud */}
        <div className="mb-3">
          <label>Latitude:</label>
          <input
            type="number"
            step="any"
            className="form-control"
            value={project.latitude !== null ? project.latitude : ''}
            onChange={(e) => setProject({ ...project, latitude: e.target.value })}
          />
        </div>
        {/* Longitud */}
        <div className="mb-3">
          <label>Longitude:</label>
          <input
            type="number"
            step="any"
            className="form-control"
            value={project.longitude !== null ? project.longitude : ''}
            onChange={(e) => setProject({ ...project, longitude: e.target.value })}
          />
        </div>
        {/* Superficie */}
        <div className="mb-3">
          <label>Area:</label>
          <input
            type="number"
            step="any"
            className="form-control"
            value={project.area !== null ? project.area : ''}
            onChange={(e) => setProject({ ...project, area: e.target.value })}
          />
        </div>
        {/* Profundidad */}
        <div className="mb-3">
          <label>Depth:</label>
          <input
            type="number"
            step="any"
            className="form-control"
            value={project.depth !== null ? project.depth : ''}
            onChange={(e) => setProject({ ...project, depth: e.target.value })}
          />
        </div>
        {/* Volumen */}
        <div className="mb-3">
          <label>Volume:</label>
          <input
            type="number"
            step="any"
            className="form-control"
            value={project.volume !== null ? project.volume : ''}
            onChange={(e) => setProject({ ...project, volume: e.target.value })}
          />
        </div>
        <button type="submit" className="btn btn-primary">
          Update Project
        </button>
      </form>
    </div>
  );
}

export default ProjectEdit;
