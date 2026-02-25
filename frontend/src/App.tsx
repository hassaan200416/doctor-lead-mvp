/*
FILE PURPOSE:
This is the root component of the entire frontend application.
It handles app-level routing based on whether the user is logged in.

WHAT IT DOES:
- Checks localStorage for a saved API key
- If user has an API key: shows the LeadsPage
- If user doesn't have an API key: shows the LoginPage
- After login, updates state to show LeadsPage

THINK OF IT AS: The "main router" that decides what to show the user.
*/

// Import CSS styles for this component
import "./App.css";
// Import React hooks
import { useEffect, useState } from "react";
// Import page components
import { LeadsPage } from "./pages/LeadsPage";
import { LoginPage } from "./pages/LoginPage";

/**
 * App component: Root component that handles routing between Login and Leads pages.
 */
function App() {
  // State: The current API key (null = not logged in, string = logged in)
  const [apiKey, setApiKey] = useState<string | null>(null);

  // Effect: Run once when app loads
  useEffect(() => {
    // Check if there's a saved API key in localStorage from previous login
    const stored = localStorage.getItem("apiKey");
    if (stored) {
      // User was previously logged in, restore their session
      setApiKey(stored);
    }
  }, []); // Empty dependency array = run once on load

  // If user doesn't have an API key, show login page
  if (!apiKey) {
    // setApiKey is called when user logs in successfully
    return <LoginPage onLogin={setApiKey} />;
  }

  // If user has an API key, show the leads page
  return <LeadsPage />;
}

export default App;
