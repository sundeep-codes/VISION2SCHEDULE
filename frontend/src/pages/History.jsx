import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const History = () => {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const response = await api.get('/events/');
                setEvents(response.data);
            } catch (err) {
                setError('Failed to load history.');
            } finally {
                setLoading(false);
            }
        };
        fetchHistory();
    }, []);

    const handleEventClick = (event) => {
        navigate('/results', { state: { eventData: event } });
    };

    return (
        <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h1>Scan History</h1>
                <button
                    onClick={() => navigate('/scan')}
                    style={{ padding: '8px 15px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                >
                    New Scan
                </button>
            </div>

            {loading && (
                <div style={{ textAlign: 'center', padding: '40px' }}>
                    <div className="loader">Loading your scan history...</div>
                </div>
            )}


            {error && (
                <div style={{ padding: '15px', backgroundColor: '#f8d7da', color: '#721c24', borderRadius: '4px', marginBottom: '20px' }}>
                    {error}
                </div>
            )}

            {!loading && events.length === 0 && (
                <div style={{ textAlign: 'center', padding: '40px', color: '#666', border: '1px dashed #ccc', borderRadius: '8px' }}>
                    No saved events found. Start by scanning a flyer!
                </div>
            )}

            {!loading && events.length > 0 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                    {events.map((event) => (
                        <div
                            key={event.id}
                            onClick={() => handleEventClick(event)}
                            style={{
                                padding: '15px',
                                border: '1px solid #ddd',
                                borderRadius: '8px',
                                backgroundColor: '#fff',
                                cursor: 'pointer',
                                transition: 'background-color 0.2s'
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f8f9fa'}
                            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#fff'}
                        >
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                <div>
                                    <h3 style={{ margin: '0 0 5px 0', color: '#333' }}>{event.title || 'Untitled Event'}</h3>
                                    <p style={{ margin: 0, fontSize: '0.9em', color: '#666' }}>📍 {event.venue || 'No venue'}</p>
                                </div>
                                <div style={{ textAlign: 'right' }}>
                                    <div style={{ fontWeight: 'bold', color: '#007bff' }}>📅 {event.date || 'No date'}</div>
                                    <div style={{ fontSize: '0.8em', color: '#999', marginTop: '5px' }}>
                                        Score: {event.confidence_score}%
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default History;
