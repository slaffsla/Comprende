import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";

// Suppress ResizeObserver loop errors that commonly occur with Select components
const resizeObserverErrorHandler = (e) => {
  if (e.message === 'ResizeObserver loop completed with undelivered notifications.' || 
      e.message === 'ResizeObserver loop limit exceeded') {
    const resizeObserverErr = document.getElementById('webpack-dev-server-client-overlay');
    if (resizeObserverErr) {
      resizeObserverErr.style.display = 'none';
    }
    e.stopImmediatePropagation();
    return true;
  }
  return false;
};

// Add global error handlers
window.addEventListener('error', resizeObserverErrorHandler);
window.addEventListener('unhandledrejection', (e) => {
  if (e.reason?.message?.includes('ResizeObserver')) {
    e.preventDefault();
  }
});

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
