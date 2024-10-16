import React, { useState, useEffect } from 'react';
import api from '../api/api';
import { useNavigate } from 'react-router-dom';
import Select from 'react-select';

function StudyCreate() {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [datasets, setDatasets] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState(null);
  const [name, setName] = useState('');
  const [timeSpace, setTimeSpace] = useState('MONTHLY');
  const [windowSize, setWindowSize] = useState(12);
  const navigate = useNavigate();

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

  // Obtener los datasets cuando se selecciona un proyecto
  useEffect(() => {
    if (selectedProject) {
      fetchDatasets(selectedProject.value);
    } else {
      setDatasets([]);
      setSelectedDataset(null);
    }
  }, [selectedProject]);

  const fetchDatasets = async (projectId) => {
    try {
      const response = await api.get('/datasets/', {
        params: { project_id: projectId },
      });
      const options = response.data.map((dataset) => ({
        value: dataset.id,
        label: dataset.name,
      }));
      setDatasets(options);
    } catch (error) {
      console.error('Error fetching datasets:', error);
      alert('Failed to fetch datasets');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedProject) {
      alert('Please select a project');
      return;
    }
    if (!selectedDataset) {
      alert('Please select a dataset');
      return;
    }
    if (!name.trim()) {
      alert('Please enter a name for the study');
      return;
    }

    try {
      await api.post('/studies', {
        name: name.trim(),
        project_id: selectedProject.value,
        dataset_id: selectedDataset.value,
        time_space: timeSpace,
        window_size: windowSize,
      });
      alert('Study created successfully');
      navigate('/studies');
    } catch (error) {
      console.error('Error creating study:', error);
      alert('Failed to create study');
    }
  };

  return (
    <div>
      <h2>Create Study</h2>
      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <label>Select Project:</label>
          <Select
            options={projects}
            value={selectedProject}
            onChange={setSelectedProject}
            placeholder="Select a project..."
            isClearable
          />
        </div>
        {selectedProject && (
          <>
            <div className="mb-3">
              <label>Select Dataset:</label>
              <Select
                options={datasets}
                value={selectedDataset}
                onChange={setSelectedDataset}
                placeholder="Select a dataset..."
                isClearable
              />
            </div>
            <div className="mb-3">
              <label htmlFor="name" className="form-label">
                Study Name
              </label>
              <input
                type="text"
                id="name"
                className="form-control"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>
            <div className="mb-3">
              <label htmlFor="timeSpace" className="form-label">
                Time Space
              </label>
              <select
                id="timeSpace"
                className="form-select"
                value={timeSpace}
                onChange={(e) => setTimeSpace(e.target.value)}
                required
              >
                <option value="DAILY">Daily</option>
                <option value="WEEKLY">Weekly</option>
                <option value="MONTHLY">Monthly</option>
              </select>
            </div>
            <div className="mb-3">
              <label htmlFor="windowSize" className="form-label">
                Window Size
              </label>
              <input
                type="number"
                id="windowSize"
                className="form-control"
                value={windowSize}
                onChange={(e) => setWindowSize(parseInt(e.target.value))}
                min="1"
                required
              />
            </div>
            <button type="submit" className="btn btn-primary">
              Create Study
            </button>
          </>
        )}
      </form>
    </div>
  );
}

export default StudyCreate;
