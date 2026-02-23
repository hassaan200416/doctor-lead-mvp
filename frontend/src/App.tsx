import './App.css';
import { useEffect, useState } from 'react';
import { LeadsPage } from './pages/LeadsPage';
import { LoginPage } from './pages/LoginPage';

function App() {
  const [apiKey, setApiKey] = useState<string | null>(null);

  useEffect(() => {
    const stored = localStorage.getItem('apiKey');
    if (stored) {
      setApiKey(stored);
    }
  }, []);

  if (!apiKey) {
    return <LoginPage onLogin={setApiKey} />;
  }

  return <LeadsPage />;
}

export default App;


