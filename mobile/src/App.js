import React, { useState, useMemo } from 'react';
import Login from './Login';
import AdminDashboard from './AdminDashboard';
import { jwtDecode } from "jwt-decode";
import EmployeeDashboard from './EmployeeDashboard';


function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));

  const role = useMemo(() => {
    if (!token) return null;
    try {
      const decoded = jwtDecode(token);
      return decoded.role;
    } catch (error) {
      console.error("Invalid token", error);
      return null;
    }
  }, [token]);

  return (
    <div className="App">
      {!token ? (
        <Login setToken={setToken} />
      ) : role === 'admin' ? (
        <AdminDashboard setToken={setToken} />
      ) : (
        <EmployeeDashboard setToken={setToken} />
      )}
    </div>
  );
}


export default App;