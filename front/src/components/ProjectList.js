// src/components/ProjectList.js
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/api';

function ProjectList() {
  const [projects, setProjects] = useState([]);

  const fetchProjects = async () => {
    try {
      const response = await api.get('/projects/');
      setProjects(response.data);
    } catch (error) {
      console.error('Error fetching projects:', error);
      alert('Failed to fetch projects');
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this project?')) {
      try {
        await api.delete(`/projects/${id}`);
        setProjects(projects.filter((project) => project.id !== id));
      } catch (error) {
        console.error('Error deleting project:', error);
        alert('Failed to delete project');
      }
    }
  };

  return (
    <div>
      <h2>Projects</h2>
      <Link to="/projects/create" className="btn btn-primary mb-3">
        Create New Project
      </Link>
      <table className="table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Longitude</th>
            <th>Latitude</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {projects.map((project) => (
            <tr key={project.id}>
              <td>{project.name}</td>
              <td>{project.longitude}</td>
              <td>{project.latitude}</td>
              <td>
                <Link
                  to={`/projects/edit/${project.id}`}
                  className="btn btn-secondary btn-sm me-2"
                >
                  Edit
                </Link>
                <button
                  onClick={() => handleDelete(project.id)}
                  className="btn btn-danger btn-sm"
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
          {projects.length === 0 && (
            <tr>
              <td colSpan="3">No projects found.</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

export default ProjectList;
