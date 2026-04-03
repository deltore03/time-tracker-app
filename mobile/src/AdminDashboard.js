import React, { useState, useEffect } from 'react';
import axios from 'axios';
// IMPORTANT: Ensure EmployeeDashboard.js exists in the same folder
import EmployeeDashboard from './EmployeeDashboard'; 

const AdminDashboard = ({ setToken }) => {
  // Fixes 'view' and 'setView' is not defined errors
  const [view, setView] = useState('admin'); 
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get('http://localhost:8000/auth/admin/all-logs', {
          headers: { Authorization: `Bearer ${token}` }
        });
        setLogs(response.data);
      } catch (err) {
        setError(err.response?.status === 403 ? "Access Denied" : "Failed to load logs");
      }
    };
    fetchLogs();
  }, []);

  const handleDelete = async (logId) => {
    if (!window.confirm("Are you sure?")) return;
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`http://localhost:8000/auth/admin/logs/${logId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setLogs(logs.filter(log => log.id !== logId));
    } catch (err) {
      alert("Delete failed");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
  };

  // Fixes the 'rreturn' typo
  return (
    <div style={styles.container}>
      <div style={styles.toggleContainer}>
        <button 
          onClick={() => setView(view === 'admin' ? 'employee' : 'admin')}
          style={styles.switchBtn}
        >
          {view === 'admin' ? 'Switch to My Clock' : 'Switch to Admin Panel'}
        </button>
        <button onClick={handleLogout} style={styles.logoutBtn}>Logout</button>
      </div>

      {view === 'admin' ? (
        <div>
          <h1>Admin Logs</h1>
          {error ? <p style={{color: 'red'}}>{error}</p> : (
            <table style={styles.table}>
              <thead>
                <tr style={styles.tableHeader}>
                  <th style={styles.th}>Employee</th>
                  <th style={styles.th}>Date</th>
                  <th style={styles.th}>Clock In</th>
                  <th style={styles.th}>Clock Out</th>
                  <th style={styles.th}>Total</th>
                  <th style={styles.th}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <tr key={log.id} style={styles.tr}>
                    <td style={styles.td}>{log.username}</td>
                    <td style={styles.td}>{log.date}</td>
                    <td style={styles.td}>{log.clock_in}</td>
                    <td style={styles.td}>{log.clock_out}</td>
                    <td style={styles.td}>{log.total_hours}h</td>
                    <td style={styles.td}>
                      <button onClick={() => handleDelete(log.id)} style={styles.deleteBtn}>Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      ) : (
        /* Fixes 'EmployeeDashboard' is not defined */
        <EmployeeDashboard setToken={setToken} />
      )}
    </div>
  );
};

const styles = {
  container: { padding: '40px', maxWidth: '1000px', margin: '0 auto', fontFamily: 'sans-serif' },
  toggleContainer: { display: 'flex', justifyContent: 'flex-end', gap: '10px', marginBottom: '20px' },
  switchBtn: { padding: '8px 16px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' },
  logoutBtn: { padding: '8px 16px', cursor: 'pointer', borderRadius: '4px', border: '1px solid #ccc', backgroundColor: '#fff' },
  table: { width: '100%', borderCollapse: 'collapse' },
  tableHeader: { backgroundColor: '#333', color: 'white' },
  th: { padding: '12px', textAlign: 'left' },
  td: { padding: '12px', borderBottom: '1px solid #ddd' },
  deleteBtn: { color: 'red', border: '1px solid red', background: 'none', padding: '4px 8px', borderRadius: '4px', cursor: 'pointer' }
};

// Fixes 'export default was not found'
export default AdminDashboard;