// src/components/ProjectSelector.js
import React, { useEffect, useState, useContext } from 'react';
import api from '../api/api';
import { ProjectContext } from '../contexts/ProjectContext';

function ProjectSelector() {
  const [projects, setProjects] = useState([]);
  const { activeProject, setActiveProject } = useContext(ProjectContext);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const response = await api.get('/projects/');
        setProjects(response.data);
      } catch (error) {
        console.error('Error fetching projects:', error);
        alert('Failed to fetch projects');
      }
    };

    fetchProjects();
  }, []);

  const handleChange = (e) => {
    const projectId = e.target.value;
    const project = projects.find((p) => p.id === projectId);
    setActiveProject(project);
  };

  return (
    <div className="mb-3">
      <label>Select Project:</label>
      <select
        className="form-select"
        value={activeProject ? activeProject.id : ''}
        onChange={handleChange}
      >
        <option value="">-- Select a Project --</option>
        {projects.map((project) => (
          <option key={project.id} value={project.id}>
            {project.name}
          </option>
        ))}
      </select>
    </div>
  );
}

export default ProjectSelector;
