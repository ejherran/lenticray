// src/components/NumericEditor.js

import React, { useState, useEffect, useRef } from 'react';
import { textEditor } from 'react-data-grid';

function NumericEditor({ row, column, onRowChange, onClose }) {
  const [value, setValue] = useState(row[column.key] ?? '');
  const inputRef = useRef(null);

  useEffect(() => {
    inputRef.current.focus();
  }, []);

  const handleChange = (event) => {
    const newValue = event.target.value;
    // Permitir números, signo negativo y punto decimal
    if (/^-?\d*(\.\d*)?$/.test(newValue) || newValue === '') {
      setValue(newValue);
    }
  };

  const handleBlur = () => {
    let sanitizedValue = value !== '' ? parseFloat(value) : null;
    onRowChange({ ...row, [column.key]: sanitizedValue }, true);
    onClose();
  };

  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      event.preventDefault(); // Evitar el comportamiento predeterminado
      inputRef.current.blur(); // Disparar el evento onBlur
    }
    if (event.key === 'Escape') {
      event.preventDefault();
      onClose(); // Cerrar el editor sin guardar cambios
    }
  };

  return (
    <input
      ref={inputRef}
      className={textEditor.className}
      value={value}
      onChange={handleChange}
      onBlur={handleBlur}
      onKeyDown={handleKeyDown} // Añadido el manejador de teclas
      type="number"
      step="0.000001" // Permitir al menos seis decimales
    />
  );
}

export default NumericEditor;
