// src/components/DatasetEdit.js
import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import api from '../api/api';
import Select from 'react-select';

function DatasetEdit() {
  const [dataset, setDataset] = useState(null);
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [variables, setVariables] = useState([]);
  const [selectedVariables, setSelectedVariables] = useState([]);
  const { id } = useParams();
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

    const fetchDataset = async () => {
      try {
        const response = await api.get(`/datasets/${id}`);
        setDataset(response.data);
        setSelectedVariables(
          response.data.variables.map((v) => ({
            value: v.id,
            label: `${v.id} - ${v.name} (${v.unit})`,
            description: v.description,
          }))
        );

        // Obtener el proyecto asociado al dataset
        const projectResponse = await api.get(`/projects/${response.data.project_id}`);
        const projectOption = {
          value: projectResponse.data.id,
          label: projectResponse.data.name,
        };
        setSelectedProject(projectOption);
      } catch (error) {
        console.error('Error fetching dataset:', error);
        alert('Failed to fetch dataset');
      }
    };

    fetchProjects();
    fetchVariables();
    fetchDataset();
  }, [id]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedProject) {
      alert('Please select a project.');
      return;
    }
    try {
      await api.put(`/datasets/${id}`, {
        name: dataset.name,
        variable_ids: selectedVariables.map((v) => v.value),
      });
      alert('Dataset updated successfully');
      navigate('/datasets');
    } catch (error) {
      console.error('Error updating dataset:', error);
      alert('Failed to update dataset');
    }
  };

  if (!dataset) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h2>Edit Dataset: {dataset.name}</h2>
      <form onSubmit={handleSubmit}>
        {/* Nombre */}
        <div className="mb-3">
          <label>Name:</label>
          <input
            type="text"
            className="form-control"
            required
            value={dataset.name}
            onChange={(e) => setDataset({ ...dataset, name: e.target.value })}
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
            isDisabled
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
            isDisabled
          />
        </div>
        <button type="submit" className="btn btn-primary">
          Update Dataset
        </button>
      </form>
    </div>
  );
}

export default DatasetEdit;
