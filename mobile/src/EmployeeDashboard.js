import React, { useState, useEffect } from 'react';
import axios from 'axios';

const EmployeeDashboard = ({ setToken }) => {
  const [isClockedIn, setIsClockedIn] = useState(false);
  const [clockInTime, setClockInTime] = useState(null);
  const [weeklyData, setWeeklyData] = useState({ total_hours: 0, entries: [] });
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      // Get Status
      const statusRes = await axios.get('http://localhost:8000/auth/status', { headers });
      setIsClockedIn(statusRes.data.clocked_in);
      setClockInTime(statusRes.data.clock_in_time);

      // Get Weekly Summary
      const weekRes = await axios.get('http://localhost:8000/auth/week', { headers });
      setWeeklyData(weekRes.data);

    } catch (err) {
      console.error("Fetch failed", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);
  const handleLogout = () => {
  localStorage.removeItem('token');
  setToken(null); // This triggers the switch back to the Login screen in App.js
};
  const handleClockAction = async () => {
    const endpoint = isClockedIn ? 'clock-out' : 'clock-in';
    try {
      const token = localStorage.getItem('token');
      await axios.post(`http://localhost:8000/auth/${endpoint}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      // Refresh everything so the table and button update
      fetchData(); 
    } catch (err) {
      alert(err.response?.data?.detail || "Action failed");
    }
  };

  if (loading) return <p>Loading your profile...</p>;

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2>Your Time Clock</h2>
        <div style={styles.statusBadge}>
           Status: <span style={{ color: isClockedIn ? '#28a745' : '#666' }}>
            {isClockedIn ? "● Working" : "○ Off-Clock"}
           </span>
        </div>
        <button onClick={handleLogout} style={styles.logoutBtn}>
            Logout
        </button>
        <button 
          onClick={handleClockAction} 
          style={{...styles.mainBtn, backgroundColor: isClockedIn ? '#dc3545' : '#28a745'}}
        >
          {isClockedIn ? "STOP SHIFT" : "START SHIFT"}
        </button>

        <hr style={styles.divider} />

        <h3>This Week: {weeklyData.total_hours} Hours</h3>
        <div style={styles.tableContainer}>
          <table style={styles.miniTable}>
            <thead>
              <tr>
                <th>Date</th>
                <th>In</th>
                <th>Out</th>
                <th>Total</th>
              </tr>
            </thead>
            <tbody>
              {weeklyData.entries.map((entry) => (
                <tr key={entry.id}>
                  <td>{entry.date}</td>
                  <td>{entry.clock_in ? new Date(entry.clock_in).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : '-'}</td>
                  <td>{entry.clock_out ? new Date(entry.clock_out).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : 'Active'}</td>
                  <td>{entry.total_hours || 0}h</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

const styles = {
    container: { padding: '20px', display: 'flex', justifyContent: 'center' },
    card: { background: '#fff', padding: '30px', borderRadius: '15px', boxShadow: '0 10px 25px rgba(0,0,0,0.05)', width: '100%', maxWidth: '500px' },
    statusBadge: { marginBottom: '20px', fontWeight: 'bold' },
    mainBtn: { width: '100%', padding: '15px', color: '#fff', border: 'none', borderRadius: '8px', fontSize: '1.1rem', cursor: 'pointer', fontWeight: 'bold' },
    divider: { margin: '25px 0', border: '0', borderTop: '1px solid #eee' },
    tableContainer: { maxHeight: '250px', overflowY: 'auto' },
    miniTable: { width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' },
    logoutBtn: {
    marginTop: '20px',
    padding: '10px',
    width: '100%',
    background: 'none',
    border: '1px solid #ddd',
    borderRadius: '8px',
    color: '#888',
    cursor: 'pointer',
    fontSize: '0.9rem'
}};


export default EmployeeDashboard;

