// src/components/DateEditor.js

import React, { useState, useEffect, useRef } from 'react';
import { textEditor } from 'react-data-grid';

function DateEditor({ row, column, onRowChange, onClose }) {
  const [value, setValue] = useState(row[column.key] ?? '');
  const inputRef = useRef(null);

  useEffect(() => {
    inputRef.current.focus();
  }, []);

  const handleChange = (event) => {
    setValue(event.target.value);
  };

  const handleBlur = () => {
    onRowChange({ ...row, [column.key]: value }, true);
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
      type="date"
      className={textEditor.className}
      value={value}
      onChange={handleChange}
      onBlur={handleBlur}
      onKeyDown={handleKeyDown} // Añadido el manejador de teclas
      pattern="\d{4}-\d{2}-\d{2}"
    />
  );
}

export default DateEditor;