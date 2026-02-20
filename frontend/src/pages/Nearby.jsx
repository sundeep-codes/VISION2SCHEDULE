import React, { useState, useEffect, useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import api from '../services/api';

const Nearby = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const initialVenue = location.state?.venue || '';
    const initialCategory = location.state?.category || '';

    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(false);
    const [showAll, setShowAll] = useState(false);
    const [error, setError] = useState('');

    const fetchNearby = useCallback(async () => {
        if (!initialVenue) return;

        setLoading(true);
        setError('');

        try {
            const response = await api.get('/nearby/', {
                params: {
                    venue: initialVenue,
                    category: initialCategory,
                    show_all: showAll
                }
            });
            setEvents(response.data || []);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to fetch nearby events.');
        } finally {
            setLoading(false);
        }
    }, [initialVenue, initialCategory, showAll]);

    useEffect(() => {
        fetchNearby();
    }, [fetchNearby]);

    return (
        <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h1>Nearby Discovery</h1>
                <button
                    onClick={() => navigate(-1)}
                    style={{ padding: '8px 15px', cursor: 'pointer', backgroundColor: '#f0f0f0', border: '1px solid #ccc', borderRadius: '4px' }}
                >
                    Back
                </button>
            </div>

            <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#f9f9f9', borderRadius: '8px', border: '1px solid #eee' }}>
                <p style={{ margin: 0 }}><strong>Searching near:</strong> {initialVenue}</p>
                <p style={{ margin: '5px 0 0 0', fontSize: '0.9em', color: '#666' }}>Category: {initialCategory || 'All'}</p>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '20px' }}>
                <button
                    onClick={() => setShowAll(!showAll)}
                    style={{
                        padding: '10px 20px',
                        backgroundColor: showAll ? '#007bff' : '#fff',
                        color: showAll ? '#fff' : '#007bff',
                        border: '2px solid #007bff',
                        borderRadius: '25px',
                        cursor: 'pointer',
                        fontWeight: 'bold',
                        transition: 'all 0.2s'
                    }}
                >
                    {showAll ? 'Showing All Nearby' : 'Showing Related Category'}
                </button>
            </div>

            {loading && <div style={{ textAlign: 'center', padding: '40px' }}>Searching for events...</div>}

            {error && (
                <div style={{ padding: '15px', backgroundColor: '#f8d7da', color: '#721c24', borderRadius: '4px', marginBottom: '20px' }}>
                    {error}
                </div>
            )}

            {!loading && !error && events.length === 0 && (
                <div style={{ textAlign: 'center', padding: '40px', color: '#666', border: '1px dashed #ccc', borderRadius: '8px' }}>
                    No nearby events found. Try toggling "Show All Nearby".
                </div>
            )}

            {!loading && events.length > 0 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                    {events.map((event, index) => (
                        <div key={index} style={{ padding: '15px', border: '1px solid #ddd', borderRadius: '8px', backgroundColor: '#fff', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                            <h3 style={{ margin: '0 0 10px 0', color: '#007bff' }}>{event.title}</h3>
                            <div style={{ fontSize: '0.9em', color: '#444' }}>
                                <p style={{ margin: '0 0 5px 0' }}>📍 {event.venue}</p>
                                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                    <span>📏 Distance: {event.distance ? `${event.distance.toFixed(1)} km` : 'N/A'}</span>
                                    {event.date && <span style={{ fontWeight: 'bold' }}>📅 {event.date}</span>}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default Nearby;
