// src/index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
import AppRouter from './components/AppRouter';
import './global.css';
import 'react-data-grid/lib/styles.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import 'bootstrap-icons/font/bootstrap-icons.css';

const container = document.getElementById('root');
const root = ReactDOM.createRoot(container);
root.render(<AppRouter />);