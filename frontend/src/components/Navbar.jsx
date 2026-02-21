import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';

const Navbar = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const token = localStorage.getItem('token');

    // Don't show Navbar on Login or Register pages
    const isAuthPage = ['/login', '/register'].includes(location.pathname);
    if (!token || isAuthPage) return null;

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    return (
        <nav style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '10px 40px',
            backgroundColor: '#2c3e50',
            color: 'white',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            position: 'sticky',
            top: 0,
            zIndex: 1000
        }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                <Link to="/scan" style={{ color: 'white', textDecoration: 'none' }}>Vision2Schedule</Link>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '25px' }}>
                <Link
                    to="/scan"
                    style={{
                        color: 'white',
                        textDecoration: location.pathname === '/scan' ? 'underline' : 'none',
                        fontWeight: location.pathname === '/scan' ? 'bold' : 'normal'
                    }}
                >
                    Scan
                </Link>
                <Link
                    to="/history"
                    style={{
                        color: 'white',
                        textDecoration: location.pathname === '/history' ? 'underline' : 'none',
                        fontWeight: location.pathname === '/history' ? 'bold' : 'normal'
                    }}
                >
                    History
                </Link>
                <button
                    onClick={handleLogout}
                    style={{
                        backgroundColor: '#e74c3c',
                        color: 'white',
                        border: 'none',
                        padding: '8px 15px',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontWeight: 'bold',
                        transition: 'background-color 0.2s'
                    }}
                    onMouseEnter={(e) => e.target.style.backgroundColor = '#c0392b'}
                    onMouseLeave={(e) => e.target.style.backgroundColor = '#e74c3c'}
                >
                    Logout
                </button>
            </div>
        </nav>
    );
};

export default Navbar;
