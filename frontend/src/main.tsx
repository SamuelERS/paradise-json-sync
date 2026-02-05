/**
 * Main Entry Point (Punto de Entrada Principal)
 *
 * Application bootstrap with React 18.
 * Inicialización de la aplicación con React 18.
 */
import React from 'react';
import ReactDOM from 'react-dom/client';
import { App } from './App';
import './styles/index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
