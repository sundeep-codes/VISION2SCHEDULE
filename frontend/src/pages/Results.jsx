import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const Results = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const eventData = location.state?.eventData || {};

    const detailItem = (label, value) => (
        <div style={{ marginBottom: '12px', borderBottom: '1px solid #eee', paddingBottom: '8px' }}>
            <span style={{ fontWeight: 'bold', color: '#555', minWidth: '100px', display: 'inline-block' }}>{label}:</span>
            <span style={{ marginLeft: '10px', color: '#000' }}>{value || 'Not found'}</span>
        </div>
    );

    return (
        <div style={{ padding: '20px', maxWidth: '800px', margin: '40px auto', backgroundColor: '#fff', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
            <h1 style={{ textAlign: 'center', color: '#333' }}>Event Details</h1>

            <div style={{ padding: '20px', border: '1px solid #e0e0e0', borderRadius: '8px', marginTop: '20px' }}>
                {detailItem('Title', eventData.title)}
                {detailItem('Date', eventData.date)}
                {detailItem('Time', eventData.time)}
                {detailItem('Venue', eventData.venue)}
                {detailItem('Organizer', eventData.organizer)}
                {detailItem('Contact', eventData.contact)}
                {detailItem('Website', eventData.website)}
                {detailItem('Category', eventData.category)}
            </div>

            <div style={{ display: 'flex', gap: '15px', marginTop: '30px' }}>
                <button
                    onClick={() => navigate('/scan')}
                    style={{ flex: 1, padding: '12px', backgroundColor: '#f0f0f0', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
                >
                    Scan Another
                </button>
            </div>
        </div>
    );
};


export default Results;
