/*
FILE PURPOSE:
This file sets up the HTTP client (Axios) that the frontend uses to talk to the backend.
It automatically adds the API key to every request and handles authentication errors.

WHAT IT DOES:
- Creates an Axios instance configured to talk to the backend
- Automatically adds the API key from localStorage to every request
- If the API key is invalid (401 error), clears it and sends user back to login

THINK OF IT AS: The "communication channel" between frontend and backend.
*/

// Import Axios library and its type definitions
import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios';

// The backend server address - change this if backend runs on a different address
const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

// Create the Axios client with default settings
export const apiClient = axios.create({
  // Use this base URL for all API requests
  baseURL: API_BASE_URL,
  // Send JSON data in all requests
  headers: {
    'Content-Type': 'application/json',
  },
  // Give up on requests that take more than 10 seconds
  timeout: 10000,
});

// Add a "request interceptor" - this runs before EVERY request
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  // Get the API key that was saved to localStorage during login
  const apiKey = localStorage.getItem('apiKey');
  
  // If we have an API key, add it to the request header
  if (apiKey) {
    // eslint-disable-next-line no-param-reassign
    config.headers['X-API-Key'] = apiKey;  // Backend checks this header
  }
  return config;  // Continue with the request
});

// Add a "response interceptor" - this runs after EVERY response
apiClient.interceptors.response.use(
  // If response is successful, just return it
  (response) => response,
  // If response has an error, handle it
  (error: AxiosError) => {
    // Check if the error is a 401 (Unauthorized - invalid API key)
    if (error.response?.status === 401) {
      // API key is invalid, so remove it from storage
      localStorage.removeItem('apiKey');
      // Set an error message for the login page to show
      localStorage.setItem('apiKeyError', 'Invalid API key. Please try again.');
      // Reload the page to go back to login
      window.location.reload();
    }
    // Pass the error to whoever called this request so they can handle it
    return Promise.reject(error);
  },
);

// Export the client so other files can use it to make API requests
export default apiClient;
