// src/components/AuthenticatedLayout.js
import React from 'react';
import Sidebar from './Sidebar';

function AuthenticatedLayout({ children }) {
  return (
    <div className='container-fluid'>
      {/* Botón para abrir offcanvas - solo visible en móviles */}
      <button
        className='btn d-md-none position-fixed m-3'
        type='button'
        data-bs-toggle='offcanvas'
        data-bs-target='#sidebar'
        style={{ zIndex: 1030, top: '-10px', left: '-10px' }}
      >
        <i className='bi bi-list fs-2'></i>
      </button>

      <div className='row min-vh-100 p-0'>
        {/* Sidebar para desktop */}
        <div 
          className='col-md-auto h-100 m-0 p-0 position-fixed d-none d-md-block' 
          style={{width: '220px'}}
        >
          <Sidebar />
        </div>

        {/* Offcanvas para móviles */}
        <div 
          className='offcanvas offcanvas-start d-md-none' 
          id='sidebar' 
          tabIndex='-1'
        >
          <div className='offcanvas-header'>
            <h5 className='offcanvas-title'>Menú</h5>
            <button 
              type='button' 
              className='btn-close' 
              data-bs-dismiss='offcanvas'
            ></button>
          </div>
          <div className='offcanvas-body'>
            <Sidebar />
          </div>
        </div>

        {/* Espaciador */}
        <div className='d-none d-md-block' style={{width: '220px'}}></div>

        {/* Contenido principal */}
        <div 
          className='col-12 col-md vh-100 p-3 overflow-auto'
        >
          {children}
        </div>
      </div>
    </div>
  );
}

export default AuthenticatedLayout;