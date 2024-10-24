import React, { useEffect, useState } from 'react';
import api from '../api/api';
import { Link } from 'react-router-dom';
import { useParams } from 'react-router-dom';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    Tooltip,
    Legend,
    ResponsiveContainer,
    CartesianGrid,
} from 'recharts';

function StudyResults() {
    const { id } = useParams();
    const [study, setStudy] = useState(null);
    const [results, setResults] = useState([]);
    const [availableColumns, setAvailableColumns] = useState([]);

    const createTitle = (col) => {
        const title_parts = col.split('_');
        return title_parts.map((part) => part.charAt(0).toUpperCase() + part.slice(1)).join(' ');
    }

    useEffect(() => {
        fetchStudy();
        fetchResults();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const fetchStudy = async () => {
        try {
            const response = await api.get(`/studies/${id}`);
            setStudy(response.data);
        } catch (error) {
            console.error('Error fetching study:', error);
            alert('Failed to fetch study');
        }
    };

    const fetchResults = async () => {
        try {
            const response = await api.get(`/studies/${id}/results`);
            setResults(response.data);

            // Obtener las columnas disponibles
            if (response.data.length > 0) {
                const columns = Object.keys(response.data[0])
                    .filter((key) => !key.endsWith('_tag'))
                    .map((key) => key);
                setAvailableColumns(columns);
            }
        } catch (error) {
            console.error('Error fetching results:', error);
            alert('Failed to fetch results');
        }
    };

    const handleDownload = async () => {
        try {
            const response = await api.get(`/studies/${id}/download_results`, {
                responseType: 'blob',
            });
            // Crear un enlace para descargar el archivo
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            const fixName = study.name.replace(/ /g, '_').toLowerCase();
            link.href = url;
            link.setAttribute('download', `study_${fixName}_results.csv`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (error) {
            console.error('Error downloading results:', error);
            alert('Failed to download results');
        }
    };

    if (!study) {
        return <div>Loading...</div>;
    }

    return (
        <div>
            <h2>Study Results</h2>
            <p>
                <strong>Name:</strong> {study.name}
            </p>
            <p>
                <strong>Status:</strong> {study.status}
            </p>
            <button onClick={handleDownload} className="btn btn-primary mb-3">
                Download Results
            </button>
            <Link
                to={`/predictions/${study.id}`}
                className="btn btn-secondary mb-3"
            >
                View Predictions
            </Link>
            <div>
                {availableColumns.map((col) => (
                    <div key={col} className="mb-5">
                        <h4>{createTitle(col)}</h4>
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={results}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="index" label={{ value: 'Observation', position: 'insideBottomRight', offset: -10 }} />
                                <YAxis domain={[0, 1]} />
                                <Tooltip
                                    formatter={(value, name, props) => {
                                        const tag = props.payload[`${col}_tag`];
                                        return [`Value: ${parseFloat(value).toFixed(4)}`, `Tag: ${tag}`];
                                    }}
                                />
                                <Legend />
                                <Line 
                                    type="monotone"
                                    dataKey={col}
                                    name={createTitle(col)}
                                    stroke="#8884d8"
                                    activeDot={{ r: 8 }} 
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default StudyResults;
