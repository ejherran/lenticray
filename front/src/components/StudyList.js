import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/api';
import Select from 'react-select';

function StudyList() {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [studies, setStudies] = useState([]);

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

  // Obtener los estudios cuando se selecciona un proyecto
  const fetchStudies = async (projectId) => {
    try {
      const response = await api.get('/studies/', {
        params: { project_id: projectId },
      });
      setStudies(response.data);
    } catch (error) {
      console.error('Error fetching studies:', error);
      alert('Failed to fetch studies');
    }
  };

  // Manejar el cambio de selección de proyecto
  const handleProjectChange = (option) => {
    setSelectedProject(option);
    if (option) {
      fetchStudies(option.value);
    } else {
      setStudies([]);
    }
  };

  // Manejar la eliminación de un estudio
  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this study?')) {
      try {
        await api.delete(`/studies/${id}`);
        setStudies(studies.filter((study) => study.id !== id));
        alert('Study deleted successfully');
      } catch (error) {
        console.error('Error deleting study:', error);
        alert('Failed to delete study');
      }
    }
  };

  // Manejar el inicio del entrenamiento de un estudio
  const handleStartTraining = async (id) => {
    if (window.confirm('Are you sure you want to start training this study?')) {
      try {
        await api.post(`/studies/${id}/start_training`);
        // Actualizar el estado del estudio localmente o volver a cargar la lista
        if (selectedProject) {
          fetchStudies(selectedProject.value);
        }
        alert('Training successfully queued.');
      } catch (error) {
        console.error('Error starting training:', error);
        alert('Failed to start training');
      }
    }
  };


  return (
    <div>
      <h2>Studies</h2>
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
      {selectedProject ? (
        <>
          <Link to="/studies/create" className="btn btn-primary mb-2">
            Create Study
          </Link>
          {studies.length > 0 ? (
            <table className="table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Dataset Name</th>
                  <th>Time Space</th>
                  <th>Window Size</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {studies.map((study) => (
                  <tr key={study.id}>
                    <td>{study.name}</td>
                    <td>{study.dataset_name || study.dataset_id}</td>
                    <td>{study.time_space}</td>
                    <td>{study.window_size}</td>
                    <td>{study.status}</td>
                    <td>
                      {study.status === 'NEW' && (
                        <>
                          <Link
                            to={`/studies/edit/${study.id}`}
                            className="btn btn-sm btn-secondary me-2"
                          >
                            Edit
                          </Link>
                          <button
                            onClick={() => handleStartTraining(study.id)}
                            className="btn btn-sm btn-success me-2"
                          >
                            Start Training
                          </button>
                        </>
                      )}
                      {study.status === 'TRAINED' && (
                        <Link
                          to={`/studies/results/${study.id}`}
                          className="btn btn-sm btn-primary me-2"
                        >
                          View Results
                        </Link>
                      )}
                      {!['PENDING', 'TRAINING'].includes(study.status) && (
                        <button
                          onClick={() => handleDelete(study.id)}
                          className="btn btn-sm btn-danger"
                        >
                          Delete
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div>No studies found for this project.</div>
          )}
        </>
      ) : (
        <div>Please select a project to view its studies.</div>
      )}
    </div>
  );
}

export default StudyList;
