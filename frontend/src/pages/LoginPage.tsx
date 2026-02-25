/*
FILE PURPOSE:
This React component displays the login page.
Users enter their API key, which is saved to localStorage and used for all API requests.

WHAT IT DOES:
- Shows a title and login form
- User enters their API key (shown as password dots for privacy)
- When user clicks Login, saves key to localStorage and goes to LeadsPage
- Shows error message if API key was invalid and user was sent back

THINK OF IT AS: The "login page" that protects the app.
*/

// Import React hooks for state and side effects
import { useEffect, useState } from "react";

/**
 * Props (input parameters) for the LoginPage component.
 */
export interface LoginPageProps {
  // Function to call after successful login (with the API key)
  onLogin: (apiKey: string) => void;
}

/**
 * LoginPage component: Shows login form for API key entry.
 */
export function LoginPage({ onLogin }: LoginPageProps) {
  // State: what the user typed in the API key input field
  const [apiKeyInput, setApiKeyInput] = useState("");

  // State: error message to display (if any)
  const [error, setError] = useState<string | null>(null);

  // Effect: run once when component loads
  useEffect(() => {
    // Check if there's an error message stored from previous auth failure
    const storedError = localStorage.getItem("apiKeyError");
    if (storedError) {
      // Show the error message
      setError(storedError);
      // Clear it from storage so it doesn't show again on reload
      localStorage.removeItem("apiKeyError");
    }
  }, []); // Empty dependency array = run once on load

  // Handle when user submits the login form
  const handleSubmit = (event: React.FormEvent) => {
    // Prevent the browser from reloading the page
    event.preventDefault();

    // Get the API key from input and trim whitespace
    const trimmed = apiKeyInput.trim();

    // If user didn't enter anything, don't proceed
    if (!trimmed) return;

    // Save the API key to localStorage so it persists across page reloads
    localStorage.setItem("apiKey", trimmed);

    // Call the parent's onLogin callback to switch to LeadsPage
    onLogin(trimmed);
  };

  return (
    <div>
      {/* Page title */}
      <h1>Doctor Lead MVP</h1>

      {/* Error message (shows if API key was invalid) */}
      {error && <p>{error}</p>}

      {/* Login form */}
      <form onSubmit={handleSubmit}>
        {/* Label and input for API key */}
        <label htmlFor="api-key-input">
          API Key
          <input
            id="api-key-input"
            type="password" // Show as dots instead of plain text
            value={apiKeyInput} // Current value from state
            // When user types, update state
            onChange={(e) => setApiKeyInput(e.target.value)}
            placeholder="Enter your API key"
          />
        </label>
        {/* Submit button */}
        <button type="submit">Login</button>
      </form>
    </div>
  );
}

export default LoginPage;
