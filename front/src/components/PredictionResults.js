import React, { useEffect, useState } from 'react';
import api from '../api/api';
import { useParams } from 'react-router-dom';
import { Link } from 'react-router-dom';
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

function PredictionResults() {
    const { id } = useParams();
    const [prediction, setPrediction] = useState(null);
    const [results, setResults] = useState([]);
    const [availableColumns, setAvailableColumns] = useState([]);

    // Mapeo de etiquetas a valores numéricos
    const labelToValue = {
        'OLIGOTRÓFICO': 1,
        'MESOTRÓFICO': 2,
        'EUTRÓFICO': 3,
        'HIPEREUTRÓFICO': 4,
    };

    const valueToLabel = {
        1: 'OLIGOTRÓFICO',
        2: 'MESOTRÓFICO',
        3: 'EUTRÓFICO',
        4: 'HIPEREUTRÓFICO',
    };

    useEffect(() => {
        fetchPrediction();
        fetchResults();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const fetchPrediction = async () => {
        try {
            const response = await api.get(`/predictions/${id}`);
            setPrediction(response.data);
        } catch (error) {
            console.error('Error fetching prediction:', error);
            alert('Failed to fetch prediction');
        }
    };

    const fetchResults = async () => {
        try {
            const response = await api.get(`/predictions/${id}/results`);
            // Añadir índice y mapear etiquetas a valores numéricos
            const dataWithIndex = response.data.map((item, index) => {
                const eutrophicationValue = labelToValue[item.eutrophication_tag] || null;
                const eutrophicationInferredValue = labelToValue[item.eutrophication_inferred] || null;
                return {
                    ...item,
                    index: index + 1,
                    eutrophication_value: eutrophicationValue,
                    eutrophication_inferred_value: eutrophicationInferredValue,
                };
            });
            setResults(dataWithIndex);

            // Obtener las columnas disponibles
            if (response.data.length > 0) {
                const columns = Object.keys(response.data[0])
                    .filter((key) => !key.endsWith('_tag') && key !== 'eutrophication_inferred')
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
            const response = await api.get(`/predictions/${id}/download_results`, {
                responseType: 'blob',
            });
            // Crear un enlace para descargar el archivo
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            const fixName = prediction.name.replace(/ /g, '_').toLowerCase();
            link.href = url;
            link.setAttribute('download', `prediction_${fixName}_results.csv`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (error) {
            console.error('Error downloading results:', error);
            alert('Failed to download results');
        }
    };

    if (!prediction) {
        return <div>Loading...</div>;
    }

    return (
        <div>
            <h2>Prediction Results</h2>
            <p>
                <strong>Name:</strong> {prediction.name}
            </p>
            <p>
                <strong>Status:</strong> {prediction.status}
            </p>
            <button onClick={handleDownload} className="btn btn-primary mb-3">
                Download Results
            </button>
            <Link to={`/predictions/${prediction.study_id}`} className="btn btn-secondary mb-3">
                Back to Predictions
            </Link>
            <div>
                {availableColumns.map((col) => (
                    <div key={col} className="mb-5">
                        <h4>{col.charAt(0).toUpperCase() + col.slice(1)}</h4>
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={results}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis
                                    dataKey="index"
                                    label={{
                                        value: 'Observation',
                                        position: 'insideBottomRight',
                                        offset: -10,
                                    }}
                                />
                                <YAxis domain={[0, 1]} />
                                <Tooltip
                                    formatter={(value, name, props) => {
                                        const tag = props.payload[`${col}_tag`];
                                        return [`Value: ${value}`, `Tag: ${tag}`];
                                    }}
                                />
                                <Legend />
                                <Line
                                    type="monotone"
                                    dataKey={col}
                                    stroke="#8884d8"
                                    activeDot={{ r: 8 }}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                ))}

                {/* Gráfica adicional comparando 'eutrophication_tag' y 'eutrophication_inferred' */}
                {results.length > 0 && results[0].eutrophication_inferred && (
                    <div className="mb-5">
                        <h4>Comparison of Eutrophication Tags</h4>
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={results}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis
                                    dataKey="index"
                                    label={{
                                        value: 'Observación',
                                        position: 'insideBottomRight',
                                        offset: -10,
                                    }}
                                />
                                <YAxis
                                    type="number"
                                    domain={[1, 4]}
                                    allowDecimals={false}
                                    tick={false}
                                />
                                <Tooltip
                                    formatter={(value, name, props) => {
                                        const label = valueToLabel[value];
                                        return [label, name];
                                    }}
                                />
                                <Legend />
                                <Line
                                    type="monotone"
                                    dataKey="eutrophication_value"
                                    name="Eutrophication Tag"
                                    stroke="#8884d8"
                                    activeDot={{ r: 8 }}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="eutrophication_inferred_value"
                                    name="Eutrophication Inferred"
                                    stroke="#82ca9d"
                                    activeDot={{ r: 8 }}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                )}
            </div>
        </div>
    );
}

export default PredictionResults;