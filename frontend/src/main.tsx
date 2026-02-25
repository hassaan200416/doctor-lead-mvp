/*
FILE PURPOSE:
This is the entry point for the entire React application.
It's the first JavaScript file that runs when the page loads.

WHAT IT DOES:
1. Imports React and React DOM libraries
2. Finds the root HTML element (div with id="root")
3. Renders the App component into that element
4. Wraps everything in StrictMode for development warnings

THINK OF IT AS: The "bootstrap" that starts up the React application.
*/

// Import React and StrictMode (for development warnings)
import { StrictMode } from "react";
// Import React DOM library (for rendering to HTML)
import { createRoot } from "react-dom/client";
// Import global CSS styles
import "./index.css";
// Import the main App component
import App from "./App.tsx";

// Find the HTML element with id="root" and create a React root
// This is where React will render the entire app
creatRoot(document.getElementById("root")!).render(
  // StrictMode helps catch bugs during development (shows extra warnings)
  <StrictMode>
    {/* Render the main App component */}
    <App />
  </StrictMode>,
);
