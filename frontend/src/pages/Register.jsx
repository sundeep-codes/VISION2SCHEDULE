import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../services/api';

const Register = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            await api.post('/auth/register', { email, password });
            // Redirect to login after successful registration
            navigate('/login');
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to register. Email might already be in use.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ maxWidth: '400px', margin: '50px auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px' }}>
            <h2>Register</h2>
            {error && <p style={{ color: 'red' }}>{error}</p>}
            <form onSubmit={handleSubmit}>
                <div style={{ marginBottom: '15px' }}>
                    <label>Email:</label>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        style={{ width: '100%', padding: '8px', marginTop: '5px' }}
                    />
                </div>
                <div style={{ marginBottom: '15px' }}>
                    <label>Password:</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        style={{ width: '100%', padding: '8px', marginTop: '5px' }}
                    />
                </div>
                <button type="submit" disabled={loading} style={{ width: '100%', padding: '10px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                    {loading ? 'Registering...' : 'Register'}
                </button>
            </form>
            <p style={{ marginTop: '15px' }}>
                Already have an account? <Link to="/login">Login here</Link>
            </p>
        </div>
    );
};

export default Register;
