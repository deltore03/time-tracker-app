import React, { useState } from 'react';
import axios from 'axios';

const Login = ({ setToken }) => {
  // 1. State for toggling modes and storing input
  const [isRegistering, setIsRegistering] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    adminKey: '' // This maps to admin_key in your Python schema
  });

  // 2. Handle Login Logic
  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    
    // FastAPI OAuth2 expects form-data, not JSON, for the token endpoint
    const loginData = new URLSearchParams();
    loginData.append('username', formData.username);
    loginData.append('password', formData.password);

    try {
      const response = await axios.post('http://localhost:8000/auth/token', loginData);
      const token = response.data.access_token;
      localStorage.setItem('token', token);
      setToken(token); // This tells App.js to switch to Dashboard
    } catch (err) {
      setError(err.response?.data?.detail || "Invalid username or password");
    }
  };

  // 3. Handle Register Logic (The one we restored)
  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const response = await axios.post('http://localhost:8000/auth/register', {
        username: formData.username,
        password: formData.password,
        admin_key: formData.adminKey // Sending the master key
      });
      alert("Registration successful! Please log in.");
      setIsRegistering(false); // Move user to login screen
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed");
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2 style={styles.title}>{isRegistering ? 'Create Admin/Employee Account' : 'Welcome Back'}</h2>
        
        {error && <p style={styles.error}>{error}</p>}

        <form onSubmit={isRegistering ? handleRegister : handleLogin} style={styles.form}>
          <input
            type="text"
            placeholder="Username"
            style={styles.input}
            value={formData.username}
            onChange={(e) => setFormData({...formData, username: e.target.value})}
            required
          />
          <input
            type="password"
            placeholder="Password"
            style={styles.input}
            value={formData.password}
            onChange={(e) => setFormData({...formData, password: e.target.value})}
            required
          />

          {/* Only show Admin Key field during Registration */}
          {isRegistering && (
            <input
              type="text"
              placeholder="Admin Master Key (Optional)"
              style={styles.input}
              value={formData.adminKey}
              onChange={(e) => setFormData({...formData, adminKey: e.target.value})}
            />
          )}

          <button type="submit" style={styles.button}>
            {isRegistering ? 'Register' : 'Login'}
          </button>
        </form>

        <p style={styles.toggleText}>
          {isRegistering ? 'Already have an account?' : 'Need an account?'} 
          <span 
            style={styles.toggleLink} 
            onClick={() => setIsRegistering(!isRegistering)}
          >
            {isRegistering ? ' Log In' : ' Register Here'}
          </span>
        </p>
      </div>
    </div>
  );
};

// Simple inline styles to make it look decent immediately
const styles = {
  container: { display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', backgroundColor: '#f5f5f5' },
  card: { padding: '40px', borderRadius: '8px', backgroundColor: 'white', boxShadow: '0 4px 12px rgba(0,0,0,0.1)', width: '100%', maxWidth: '400px' },
  title: { textAlign: 'center', marginBottom: '24px', color: '#333' },
  form: { display: 'flex', flexDirection: 'column', gap: '15px' },
  input: { padding: '12px', borderRadius: '4px', border: '1px solid #ddd', fontSize: '16px' },
  button: { padding: '12px', borderRadius: '4px', border: 'none', backgroundColor: '#007bff', color: 'white', fontSize: '16px', cursor: 'pointer', fontWeight: 'bold' },
  error: { color: 'red', textAlign: 'center', fontSize: '14px' },
  toggleText: { textAlign: 'center', marginTop: '20px', fontSize: '14px' },
  toggleLink: { color: '#007bff', cursor: 'pointer', fontWeight: 'bold' }
};

export default Login;