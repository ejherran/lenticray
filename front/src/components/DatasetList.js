// src/components/DatasetList.js
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/api';
import Select from 'react-select';

function DatasetList() {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [datasets, setDatasets] = useState([]);

  // Obtener la lista de proyectos al montar el componente
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

    fetchProjects();
  }, []);

  // Función para obtener los datasets cuando se selecciona un proyecto
  const fetchDatasets = async (projectId) => {
    try {
      const response = await api.get('/datasets/', {
        params: { project_id: projectId },
      });
      setDatasets(response.data);
    } catch (error) {
      console.error('Error fetching datasets:', error);
      alert('Failed to fetch datasets');
    }
  };

  // Manejar el cambio de selección de proyecto
  const handleProjectChange = (option) => {
    setSelectedProject(option);
    if (option) {
      fetchDatasets(option.value);
    } else {
      setDatasets([]);
    }
  };

  // Manejar la eliminación de un dataset
  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this dataset?')) {
      try {
        await api.delete(`/datasets/${id}`);
        setDatasets(datasets.filter((dataset) => dataset.id !== id));
      } catch (error) {
        console.error('Error deleting dataset:', error);
        alert('Failed to delete dataset');
      }
    }
  };

  return (
    <div>
      <h2>Datasets</h2>
      <div className="mb-3">
        <label>Select Project:</label>
        <Select
          options={projects}
          value={selectedProject}
          onChange={handleProjectChange}
          placeholder="Select a project..."
          isClearable
        />
      </div>
      <Link to="/datasets/create" className="btn btn-primary mb-3">
        Create New Dataset
      </Link>
      {selectedProject ? (
        datasets.length > 0 ? (
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Last Modification</th>
                <th>Rows</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {datasets.map((dataset) => (
                <tr key={dataset.id}>
                  <td>{dataset.name}</td>
                  <td>{dataset.date}</td>
                  <td>{dataset.rows}</td>
                  <td>
                    <Link
                      to={`/datasets/edit/${dataset.id}`}
                      className="btn btn-secondary btn-sm me-2"
                    >
                      Edit
                    </Link>
                    <button
                      onClick={() => handleDelete(dataset.id)}
                      className="btn btn-danger btn-sm"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div>No datasets found for this project.</div>
        )
      ) : (
        <div>Please select a project to view its datasets.</div>
      )}
    </div>
  );
}

export default DatasetList;
