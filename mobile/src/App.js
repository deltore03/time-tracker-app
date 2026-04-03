import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [adminKey, setAdminKey] = useState('');
  const [isRegistering, setIsRegistering] = useState(false);
  const [token, setToken] = useState(localStorage.getItem('token'));

  // --- REGISTRATION LOGIC ---
  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      // Note: Your FastAPI /register usually expects JSON, not FormData
      await axios.post('http://localhost:8000/auth/register', {
        username: username,
        password: password
      });
      alert("Registration Successful! Now please login.");
      setIsRegistering(false); // Send them back to the login screen
    } catch (error) {
      console.error(error);
      alert("Registration failed. User might already exist.");
    }
  };

  // --- LOGIN LOGIC (Same as before) ---
  const handleLogin = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    try {
      const response = await axios.post('http://localhost:8000/auth/token', formData);
      localStorage.setItem('token', response.data.access_token);
      setToken(response.data.access_token);
    } catch (error) {
      alert("Login failed.");
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
  };

  // 1. IF LOGGED IN
  if (token) {
    return (
      <div style={{ textAlign: 'center', marginTop: '50px' }}>
        <h1>Welcome to the Dashboard</h1>
        <button onClick={logout} style={{ color: 'red' }}>Logout</button>
      </div>
    );
  }

  // 2. IF NOT LOGGED IN (Show either Login or Register)
  return (
    <div style={{ textAlign: 'center', marginTop: '50px', fontFamily: 'sans-serif' }}>
      <h2>{isRegistering ? "Create Account" : "Please Login"}</h2>
      
      <form onSubmit={isRegistering ? handleRegister : handleLogin}>
        <input 
          type="text" 
          placeholder="Username" 
          onChange={(e) => setUsername(e.target.value)} 
          style={{ display: 'block', margin: '10px auto', padding: '10px', width: '200px' }}
        />
        <input 
          type="password" 
          placeholder="Password" 
          onChange={(e) => setPassword(e.target.value)} 
          style={{ display: 'block', margin: '10px auto', padding: '10px', width: '200px' }}
        />
        {isRegistering && (
          <div style={{ marginTop: '10px' }}>
            <label style={{ fontSize: '12px', color: 'gray' }}>Admin Setup (Optional)</label>
            <input 
              type="password" 
              placeholder="Master Key" 
              value={adminKey}
              onChange={(e) => setAdminKey(e.target.value)} 
              style={{ 
                display: 'block', 
                margin: '5px auto', 
                padding: '10px', 
                width: '200px',
                border: '1px dashed #ff4d4d' // Red dashed border to signal "Power User"
              }}
            />
          </div>
        )}
        <button type="submit" style={{ padding: '10px 20px', background: '#007bff', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>
          {isRegistering ? "Sign Up" : "Login"}
        </button>
      </form>
      
      <button 
        onClick={() => setIsRegistering(!isRegistering)} 
        style={{ marginTop: '20px', background: 'none', border: 'none', color: '#007bff', cursor: 'pointer', textDecoration: 'underline' }}
      >
        {isRegistering ? "Already have an account? Login" : "Don't have an account? Register"}
      </button>
    </div>
  );
}

export default App;