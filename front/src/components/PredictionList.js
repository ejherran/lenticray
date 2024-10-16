import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import api from '../api/api';

function PredictionList() {
    const { studyId } = useParams();
    const [study, setStudy] = useState(null);
    const [predictions, setPredictions] = useState([]);

    useEffect(() => {
        fetchStudy();
        fetchPredictions();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const fetchStudy = async () => {
        try {
            const response = await api.get(`/studies/${studyId}`);
            setStudy(response.data);
        } catch (error) {
            console.error('Error fetching study:', error);
            alert('Failed to fetch study');
        }
    };

    const fetchPredictions = async () => {
        try {
            const response = await api.get('/predictions/', {
                params: { study_id: studyId },
            });
            setPredictions(response.data);
        } catch (error) {
            console.error('Error fetching predictions:', error);
            alert('Failed to fetch predictions');
        }
    };

    const handleDelete = async (id) => {
        if (window.confirm('Are you sure you want to delete this prediction?')) {
            try {
                await api.delete(`/predictions/${id}`);
                setPredictions(predictions.filter((prediction) => prediction.id !== id));
                alert('Prediction deleted successfully');
            } catch (error) {
                console.error('Error deleting prediction:', error);
                alert('Failed to delete prediction');
            }
        }
    };

    if (!study) {
        return <div>Loading...</div>;
    }

    return (
        <div>
            <h2>Predictions for Study: {study.name}</h2>
            <Link
                to={`/predictions/create?study_id=${studyId}`}
                className="btn btn-primary mb-2"
            >
                Create Prediction
            </Link>
            {predictions.length > 0 ? (
                <table className="table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Window Size</th>
                            <th>Amount</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {predictions.map((prediction) => (
                            <tr key={prediction.id}>
                                <td>{prediction.name}</td>
                                <td>{prediction.window_size}</td>
                                <td>{prediction.amount}</td>
                                <td>{prediction.status}</td>
                                <td>
                                    {/* Mostrar el botón de eliminar solo si el estado es COMPLETE o FAILED */}
                                    {['COMPLETE', 'FAILED'].includes(prediction.status) && (
                                        <button
                                            onClick={() => handleDelete(prediction.id)}
                                            className="btn btn-sm btn-danger"
                                        >
                                            Delete
                                        </button>
                                    )}
                                    {prediction.status === 'COMPLETE' && (
                                        <Link
                                            to={`/predictions/results/${prediction.id}`}
                                            className="btn btn-sm btn-primary me-2"
                                        >
                                            View Results
                                        </Link>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            ) : (
                <div>No predictions found for this study.</div>
            )}
        </div>
    );
}

export default PredictionList;
