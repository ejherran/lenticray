import React, { useState, useEffect } from 'react';
import api from '../api/api';
import { useParams, useNavigate } from 'react-router-dom';

function StudyEdit() {
  const { id } = useParams();
  const [study, setStudy] = useState(null);
  const [name, setName] = useState('');
  const [timeSpace, setTimeSpace] = useState('daily');
  const [windowSize, setWindowSize] = useState(1);
  const navigate = useNavigate();

  useEffect(() => {
    fetchStudy();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchStudy = async () => {
    try {
      const response = await api.get(`/studies/${id}`);
      if (response.data.status !== 'NEW') {
        alert('Only studies in NEW status can be edited');
        navigate('/studies');
        return;
      }
      setStudy(response.data);
      setName(response.data.name);
      setTimeSpace(response.data.time_space);
      setWindowSize(response.data.window_size);
    } catch (error) {
      console.error('Error fetching study:', error);
      alert('Failed to fetch study');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim()) {
      alert('Please enter a name for the study');
      return;
    }
    try {
      await api.put(`/studies/${id}`, {
        name: name.trim(),
        time_space: timeSpace,
        window_size: windowSize,
      });
      alert('Study updated successfully');
      navigate('/studies');
    } catch (error) {
      console.error('Error updating study:', error);
      alert('Failed to update study');
    }
  };

  if (!study) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h2>Edit Study</h2>
      <p>
        <strong>Project ID:</strong> {study.project_id}
      </p>
      <p>
        <strong>Dataset ID:</strong> {study.dataset_id}
      </p>
      <form onSubmit={handleSubmit}>
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
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
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
        <button type="submit" className="btn btn-primary me-2">
          Save Changes
        </button>
        <button
          type="button"
          className="btn btn-secondary"
          onClick={() => navigate('/studies')}
        >
          Cancel
        </button>
      </form>
    </div>
  );
}

export default StudyEdit;
