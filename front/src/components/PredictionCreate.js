import React, { useState, useEffect } from 'react';
import api from '../api/api';
import { useNavigate, useLocation } from 'react-router-dom';

function PredictionCreate() {
  const navigate = useNavigate();
  const location = useLocation();
  const [studyId, setStudyId] = useState('');
  const [study, setStudy] = useState(null);
  const [name, setName] = useState('');
  const [windowSize, setWindowSize] = useState(12);
  const [amount, setAmount] = useState(12);

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const studyIdParam = params.get('study_id');
    if (studyIdParam) {
      setStudyId(studyIdParam);
      fetchStudy(studyIdParam);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchStudy = async (id) => {
    try {
      const response = await api.get(`/studies/${id}`);
      setStudy(response.data);
    } catch (error) {
      console.error('Error fetching study:', error);
      alert('Failed to fetch study');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!studyId) {
      alert('Study ID is required');
      return;
    }
    if (!name.trim()) {
      alert('Please enter a name for the prediction');
      return;
    }

    try {
      await api.post('/predictions', {
        name: name.trim(),
        study_id: studyId,
        window_size: windowSize,
        amount: amount,
      });
      alert('Prediction created successfully');
      navigate(`/predictions/${studyId}`);
    } catch (error) {
      console.error('Error creating prediction:', error);
      alert('Failed to create prediction');
    }
  };

  return (
    <div>
      <h2>Create Prediction</h2>
      {study && (
        <p>
          <strong>Study:</strong> {study.name}
        </p>
      )}
      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <label htmlFor="name" className="form-label">
            Prediction Name
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
        <div className="mb-3">
          <label htmlFor="amount" className="form-label">
            Amount
          </label>
          <input
            type="number"
            id="amount"
            className="form-control"
            value={amount}
            onChange={(e) => setAmount(parseInt(e.target.value))}
            min="1"
            required
          />
        </div>
        <button type="submit" className="btn btn-primary me-2">
          Create Prediction
        </button>
        <button
          type="button"
          className="btn btn-secondary"
          onClick={() => navigate(-1)}
        >
          Cancel
        </button>
      </form>
    </div>
  );
}

export default PredictionCreate;
