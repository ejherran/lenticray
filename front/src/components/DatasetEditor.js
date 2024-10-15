import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import DataGrid from 'react-data-grid';
import { textEditor } from 'react-data-grid';
import 'react-data-grid/lib/styles.css';
import api from '../api/api';
import NumericEditor from './NumericEditor';
import DateEditor from './DateEditor';

function DatasetEditor() {
  const { id } = useParams(); // Dataset ID
  const navigate = useNavigate();

  const [columns, setColumns] = useState([]);
  const [rows, setRows] = useState([]);
  const [pageSize] = useState(100);
  const [pageNumber, setPageNumber] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [changesMade, setChangesMade] = useState(false);
  const [variablesMap, setVariablesMap] = useState({}); // To store variable info including units

  const isSavingRef = useRef(false);
  const fileInputRef = useRef(null);
  const [selectedFile, setSelectedFile] = useState(null);

  useEffect(() => {
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pageNumber]);

  const fetchData = async () => {
    if (changesMade && !isSavingRef.current) {
      const confirmLeave = window.confirm(
        'You have unsaved changes. Do you want to save them before changing the page?'
      );
      if (confirmLeave) {
        await saveData();
      } else {
        setChangesMade(false);
      }
    }

    try {
      // Fetch dataset variables and units
      const datasetResponse = await api.get(`/datasets/${id}`);
      const variables = datasetResponse.data.variables; // Assuming variables is an array of objects with id, name, unit
      const variablesMapTemp = {};
      variables.forEach((variable) => {
        variablesMapTemp[variable.id] = variable;
      });
      setVariablesMap(variablesMapTemp);

      // Fetch 'Water Body' name from project
      const projectResponse = await api.get(`/projects/${datasetResponse.data.project_id}`);
      const waterBodyName = projectResponse.data.name;

      // Fetch data rows
      const response = await api.get(`/datasets/${id}/data`, {
        params: { page_size: pageSize, page_number: pageNumber },
      });
      const data = response.data;

      // Configure columns based on data keys and variables
      let columnDefs = [];

      if (data.data.length > 0) {
        const dataColumns = Object.keys(data.data[0]);
        // Remove 'Water Body' if present
        const filteredColumns = dataColumns.filter((key) => key !== 'Water Body');
        filteredColumns.forEach((key) => {
          if (key === 'Sample Date') {
            columnDefs.push(createColumnDef(key, 'date'));
          } else {
            const variable = variablesMapTemp[key];
            const unit = variable ? variable.unit : '';
            columnDefs.push(createColumnDef(key, 'variable', unit));
          }
        });
      } else {
        // If no data, define columns based on variables
        const allColumns = ['Sample Date', ...variables.map((v) => v.id)];
        allColumns.forEach((key) => {
          if (key === 'Sample Date') {
            columnDefs.push(createColumnDef(key, 'date'));
          } else {
            const variable = variablesMapTemp[key];
            const unit = variable ? variable.unit : '';
            columnDefs.push(createColumnDef(key, 'variable', unit));
          }
        });
      }

      setColumns(columnDefs);

      // Ensure rows have 100 entries and assign unique IDs
      const fetchedRows = data.data.map((row, index) => ({
        id: index,
        ...row,
        'Water Body': waterBodyName,
      }));
      const numFetchedRows = fetchedRows.length;
      const emptyRowsNeeded = pageSize - numFetchedRows;
      const emptyRowTemplate = { 'Water Body': waterBodyName };
      // For other columns, set to empty string
      columnDefs.forEach((col) => {
        if (col.key !== 'Water Body') {
          emptyRowTemplate[col.key] = '';
        }
      });
      const emptyRows = Array.from({ length: emptyRowsNeeded }, (_, idx) => ({
        id: numFetchedRows + idx,
        ...emptyRowTemplate,
      }));

      const fullRows = [...fetchedRows, ...emptyRows];

      setRows(fullRows);
      setTotalPages(data.total_pages || 1);
    } catch (error) {
      console.error('Error fetching data:', error);
      alert('Failed to fetch data');
    }
  };

  const createColumnDef = (key, columnType = 'text', unit = '') => {
    let column = {
      key: key,
      name: key,
      resizable: true,
      sortable: true,
    };

    if (columnType === 'variable') {
      column.name = `${key} (${unit})`; // Include unit in header
      column.renderEditCell = NumericEditor;
    } else if (columnType === 'date') {
      column.renderEditCell = DateEditor;
    } else {
      column.renderEditCell = textEditor;
    }

    return column;
  };

  const saveData = async () => {
    try {
      isSavingRef.current = true; // Indicate that saving has started

      // Fetch 'Water Body' name
      const datasetResponse = await api.get(`/datasets/${id}`);
      const projectResponse = await api.get(`/projects/${datasetResponse.data.project_id}`);
      const waterBodyName = projectResponse.data.name;

      // Filter rows that have data, excluding 'Water Body' and 'id'
      const nonEmptyRows = rows.filter((row) => {
        const { id, 'Water Body': waterBody, ...dataFields } = row; // Exclude 'id' and 'Water Body'
        return Object.values(dataFields).some(
          (value) => value != null && String(value).trim() !== ''
        );
      });

      if (nonEmptyRows.length === 0) {
        alert('No data to save on this page.');
        setChangesMade(false);
        isSavingRef.current = false; // Reset saving flag
        return;
      }

      // Validate and prepare data to send
      const dataToSend = [];
      for (const row of nonEmptyRows) {
        const { id, 'Water Body': waterBody, ...rest } = row;

        // Replacing '' with null
        const sanitizedRow = {};
        let hasVariableData = false;
        let hasSampleDate = false;

        for (const [key, value] of Object.entries(rest)) {
          let sanitizedValue = value !== '' ? value : null;

          if (key === 'Sample Date') {
            if (sanitizedValue != null) {
              hasSampleDate = true;
              // Validate date format YYYY-mm-dd
              const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
              if (!dateRegex.test(sanitizedValue)) {
                alert(`Sample Date in row ${id + 1} is not in the correct format (YYYY-MM-DD).`);
                isSavingRef.current = false; // Reset saving flag
                return;
              }
            }
          } else {
            // Variable columns
            if (sanitizedValue != null) {
              hasVariableData = true;
              // Validate numeric
              const numericValue = parseFloat(sanitizedValue);
              if (isNaN(numericValue)) {
                alert(`Variable '${key}' in row ${id + 1} must be numeric.`);
                isSavingRef.current = false; // Reset saving flag
                return;
              }
              sanitizedValue = numericValue;
            }
          }
          sanitizedRow[key] = sanitizedValue;
        }

        // Check if 'Sample Date' is provided if there are variable data
        if (hasVariableData && !hasSampleDate) {
          alert(`Row ${id + 1} has variable data but no Sample Date.`);
          isSavingRef.current = false; // Reset saving flag
          return;
        }

        dataToSend.push({
          'Water Body': waterBodyName,
          ...sanitizedRow,
        });
      }

      // Send data to backend
      await api.put(`/datasets/${id}/data`, {
        page_size: pageSize,
        page_number: pageNumber,
        data: dataToSend,
      });
      setChangesMade(false);
      alert('Data saved successfully.');

      // Reload current page
      await fetchData();
    } catch (error) {
      console.error('Error saving data:', error);
      alert('Failed to save data');
    } finally {
      isSavingRef.current = false; // Indicate that saving has ended
    }
  };

  const handlePageChange = async (newPageNumber) => {
    if (changesMade && !isSavingRef.current) {
      const confirmLeave = window.confirm(
        'You have unsaved changes. Do you want to save them before changing the page?'
      );
      if (confirmLeave) {
        await saveData();
      } else {
        setChangesMade(false);
      }
    }
    setPageNumber(newPageNumber);
  };

  const handleAddPage = async () => {
    if (changesMade && !isSavingRef.current) {
      const confirmLeave = window.confirm(
        'You have unsaved changes. Do you want to save them before adding a new page?'
      );
      if (confirmLeave) {
        await saveData();
      } else {
        setChangesMade(false);
      }
    }
    setPageNumber(totalPages + 1);
    setRows([]);
    setChangesMade(false);
  };

  const onRowsChange = (newRows) => {
    setRows(newRows);
    setChangesMade(true);
  };

  const onBeforeUnload = (e) => {
    if (changesMade) {
      e.preventDefault();
      e.returnValue = '';
    }
  };

  useEffect(() => {
    window.addEventListener('beforeunload', onBeforeUnload);
    return () => window.removeEventListener('beforeunload', onBeforeUnload);
  }, [changesMade]);

  const rowKeyGetter = (row) => row.id;

  // New functions for handling CSV upload
  const handleUploadClick = () => {
    if (changesMade && !isSavingRef.current) {
      const confirmProceed = window.confirm(
        'You have unsaved changes. Do you want to proceed without saving?'
      );
      if (!confirmProceed) {
        return;
      }
    }
    fileInputRef.current.click();
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      uploadCSV(file);
    }
  };

  const uploadCSV = async (file) => {
    try {
      // Mostrar mensaje de carga
      alert('Uploading CSV file. Please wait...');

      // Crear FormData y agregar el archivo
      const formData = new FormData();
      formData.append('file', file);

      // Enviar petición al backend
      await api.post(`/datasets/${id}/upload_csv`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Actualizar el estado
      setChangesMade(false);
      alert('CSV file uploaded and dataset updated successfully.');

      // Recargar los datos
      setPageNumber(1); // Reiniciar a la primera página
      await fetchData();
    } catch (error) {
      console.error('Error uploading CSV:', error);
      alert('Failed to upload CSV. Please ensure the file is valid and try again.');
    }
  };

  // Dentro de tu componente DatasetEditor.js

  const downloadCSV = async () => {
    try {
      // Realizar la petición GET
      const response = await api.get(`/datasets/${id}/download_csv`, {
        responseType: 'blob', // Importante para manejar blobs
      });

      // Crear una URL para el blob
      const url = window.URL.createObjectURL(new Blob([response.data]));

      // Crear un elemento <a> para iniciar la descarga
      const link = document.createElement('a');
      link.href = url;
      

      // Extraer el nombre del archivo del header 'Content-Disposition'
      const contentDisposition = response.headers['content-disposition'];
      let filename = 'dataset.csv';
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
        if (filenameMatch.length === 2) {
          filename = filenameMatch[1];
        }
      }
      link.setAttribute('download', filename);

      // Añadir el elemento al DOM y hacer clic en él
      document.body.appendChild(link);
      link.click();

      // Limpiar
      document.body.removeChild(link);
    } catch (error) {
      console.error('Error downloading CSV:', error);
      alert('Failed to download CSV.');
    }
  };


  return (
    <div>
      <h2>Dataset Editor</h2>
      <button onClick={() => navigate('/datasets')} className="btn btn-secondary mb-2">
        Back to Datasets
      </button>
      <button onClick={saveData} className="btn btn-primary mb-2 ms-2">
        Save Changes
      </button>
      <button onClick={handleAddPage} className="btn btn-success mb-2 ms-2">
        Add Page
      </button>
      <button onClick={handleUploadClick} className="btn btn-info mb-2 ms-2">
        Upload CSV
      </button>
      <button onClick={downloadCSV} className="btn btn-warning mb-2 ms-2">
        Download CSV
      </button>
      <input
        type="file"
        accept=".csv"
        ref={fileInputRef}
        style={{ display: 'none' }}
        onChange={handleFileChange}
      />
      <div style={{ height: '600px' }}>
        <DataGrid
          columns={columns}
          rows={rows}
          onRowsChange={onRowsChange}
          rowKeyGetter={rowKeyGetter}
          className="rdg-light"
        />
      </div>
      <div className="mt-3">
        <button
          onClick={() => handlePageChange(1)}
          disabled={pageNumber === 1}
          className="btn btn-outline-primary me-2"
        >
          {'<<'}
        </button>
        <button
          onClick={() => handlePageChange(pageNumber - 1)}
          disabled={pageNumber === 1}
          className="btn btn-outline-primary me-2"
        >
          {'<'}
        </button>
        <span>
          Page {pageNumber} of {totalPages}
        </span>
        <button
          onClick={() => handlePageChange(pageNumber + 1)}
          disabled={pageNumber >= totalPages}
          className="btn btn-outline-primary ms-2 me-2"
        >
          {'>'}
        </button>
        <button
          onClick={() => handlePageChange(totalPages)}
          disabled={pageNumber >= totalPages}
          className="btn btn-outline-primary"
        >
          {'>>'}
        </button>
      </div>
    </div>
  );
}

export default DatasetEditor;
