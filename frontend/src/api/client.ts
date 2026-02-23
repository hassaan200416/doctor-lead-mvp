import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const apiKey = localStorage.getItem('apiKey');
  if (apiKey) {
    // eslint-disable-next-line no-param-reassign
    config.headers['X-API-Key'] = apiKey;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Clear invalid key and force user back to login
      localStorage.removeItem('apiKey');
      localStorage.setItem('apiKeyError', 'Invalid API key. Please try again.');
      window.location.reload();
    }
    return Promise.reject(error);
  },
);

export default apiClient;
