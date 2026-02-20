import React from 'react';
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
    const navigate = useNavigate();

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    return (
        <div style={{ padding: '20px' }}>
            <h1>Dashboard</h1>
            <p>Welcome to your Vision2Schedule Dashboard!</p>
            <button onClick={handleLogout} style={{ padding: '10px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                Logout
            </button>
        </div>
    );
};

export default Dashboard;
