import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const Results = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const eventData = location.state?.eventData || {};

    return (
        <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
            <h1>Extraction Results</h1>
            <pre>{JSON.stringify(eventData, null, 2)}</pre>
            <button onClick={() => navigate('/scan')} style={{ marginTop: '20px' }}>
                Back to Scan
            </button>
        </div>
    );
};

export default Results;
