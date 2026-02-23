import { useEffect, useState } from 'react';

export interface LoginPageProps {
  onLogin: (apiKey: string) => void;
}

export function LoginPage({ onLogin }: LoginPageProps) {
  const [apiKeyInput, setApiKeyInput] = useState('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const storedError = localStorage.getItem('apiKeyError');
    if (storedError) {
      setError(storedError);
      localStorage.removeItem('apiKeyError');
    }
  }, []);

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    const trimmed = apiKeyInput.trim();
    if (!trimmed) return;

    localStorage.setItem('apiKey', trimmed);
    onLogin(trimmed);
  };

  return (
    <div>
      <h1>Doctor Lead MVP</h1>
      {error && <p>{error}</p>}
      <form onSubmit={handleSubmit}>
        <label htmlFor="api-key-input">
          API Key
          <input
            id="api-key-input"
            type="password"
            value={apiKeyInput}
            onChange={(e) => setApiKeyInput(e.target.value)}
            placeholder="Enter your API key"
          />
        </label>
        <button type="submit">Login</button>
      </form>
    </div>
  );
}

export default LoginPage;


