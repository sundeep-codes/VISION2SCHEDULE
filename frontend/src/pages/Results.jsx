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

    const getScoreColor = (score) => {
        if (score >= 95) return '#28a745';
        if (score >= 90) return '#ffc107';
        return '#dc3545';
    };

    const [showScheduleModal, setShowScheduleModal] = useState(false);

    const handleDownloadICS = async () => {
        try {
            // Note: This assumes eventData has been saved and has an ID
            // For now, we'll use a placeholder or trigger the API call
            const response = await api.get(`/calendar/ics/${eventData.id || 0}`, { responseType: 'blob' });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `event_${eventData.id || 'scan'}.ics`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            alert('ICS download failed. Make sure the event is saved.');
        }
    };

    const handleGoogleSync = async () => {
        try {
            const response = await api.post(`/calendar/google-sync/${eventData.id || 0}`);
            alert('Synced to Google Calendar!');
        } catch (err) {
            alert('Google Sync failed.');
        }
    };

    return (
        <div style={{ padding: '20px', maxWidth: '800px', margin: '40px auto', backgroundColor: '#fff', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '2px solid #f0f0f0', paddingBottom: '15px', marginBottom: '20px' }}>
                <h1 style={{ margin: 0, color: '#333' }}>Event Results</h1>
                <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '12px', color: '#666', fontWeight: 'bold' }}>CONFIDENCE</div>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: getScoreColor(eventData.confidence_score) }}>
                        {eventData.confidence_score ? `${eventData.confidence_score}%` : 'N/A'}
                    </div>
                </div>
            </div>

            <div style={{ padding: '20px', border: '1px solid #e0e0e0', borderRadius: '8px' }}>
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
                    style={{ flex: 1, padding: '12px', backgroundColor: '#f8f9fa', border: '1px solid #ddd', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
                >
                    Scan Another
                </button>
                <button
                    onClick={() => setShowScheduleModal(true)}
                    style={{ flex: 1, padding: '12px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
                >
                    Schedule
                </button>
                <button
                    onClick={() => navigate('/nearby', { state: { venue: eventData.venue, category: eventData.category } })}
                    style={{ flex: 1, padding: '12px', backgroundColor: '#17a2b8', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
                >
                    Discover Nearby
                </button>
            </div>

            {/* Simple Modal Overlay */}
            {showScheduleModal && (
                <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 }}>
                    <div style={{ backgroundColor: 'white', padding: '30px', borderRadius: '12px', width: '300px', textAlign: 'center' }}>
                        <h3>Add to Calendar</h3>
                        <button
                            onClick={handleDownloadICS}
                            style={{ width: '100%', padding: '10px', marginBottom: '10px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                        >
                            Download ICS File
                        </button>
                        <button
                            onClick={handleGoogleSync}
                            style={{ width: '100%', padding: '10px', marginBottom: '20px', backgroundColor: '#4285F4', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                        >
                            Sync to Google
                        </button>
                        <button
                            onClick={() => setShowScheduleModal(false)}
                            style={{ backgroundColor: 'transparent', border: 'none', color: '#666', cursor: 'pointer', textDecoration: 'underline' }}
                        >
                            Cancel
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};


export default Results;
