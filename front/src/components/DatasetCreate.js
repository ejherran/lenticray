// src/components/DatasetCreate.js
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/api';

// Importamos react-select
import Select from 'react-select';

function DatasetCreate() {
  const [name, setName] = useState('');
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [variables, setVariables] = useState([]);
  const [selectedVariables, setSelectedVariables] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const response = await api.get('/projects/');
        const options = response.data.map((project) => ({
          value: project.id,
          label: project.name,
        }));
        setProjects(options);
      } catch (error) {
        console.error('Error fetching projects:', error);
        alert('Failed to fetch projects');
      }
    };

    const fetchVariables = async () => {
      try {
        const response = await api.get('/variables/');
        const options = response.data.map((variable) => ({
          value: variable.id,
          label: `${variable.id} - ${variable.name} (${variable.unit})`,
          description: variable.description,
        }));
        setVariables(options);
      } catch (error) {
        console.error('Error fetching variables:', error);
        alert('Failed to fetch variables');
      }
    };

    fetchProjects();
    fetchVariables();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedProject) {
      alert('Please select a project.');
      return;
    }
    try {
      await api.post(
        '/datasets/',
        {
          name,
          variable_ids: selectedVariables.map((v) => v.value),
        },
        {
          params: { project_id: selectedProject.value },
        }
      );
      alert('Dataset created successfully');
      navigate('/datasets');
    } catch (error) {
      console.error('Error creating dataset:', error);
      alert('Failed to create dataset');
    }
  };

  return (
    <div>
      <h2>Create New Dataset</h2>
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
        {/* Seleccionar Proyecto */}
        <div className="mb-3">
          <label>Project:</label>
          <Select
            options={projects}
            value={selectedProject}
            onChange={(option) => setSelectedProject(option)}
            placeholder="Select a project..."
            isClearable
          />
        </div>
        {/* Variables */}
        <div className="mb-3">
          <label>Variables:</label>
          <Select
            options={variables}
            value={selectedVariables}
            onChange={(options) => setSelectedVariables(options)}
            isMulti
            placeholder="Select variables..."
          />
        </div>
        <button type="submit" className="btn btn-primary">
          Create Dataset
        </button>
      </form>
    </div>
  );
}

export default DatasetCreate;
