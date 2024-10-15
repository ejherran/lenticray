// src/index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
import AppRouter from './components/AppRouter';
import 'bootstrap/dist/css/bootstrap.min.css';
import './components/styles.css';

const container = document.getElementById('root');
const root = ReactDOM.createRoot(container);
root.render(<AppRouter />);