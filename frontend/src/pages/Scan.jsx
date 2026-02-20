import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ImageUpload from '../components/ImageUpload';
import CameraCapture from '../components/CameraCapture';
import api from '../services/api';

const Scan = () => {
    const [file, setFile] = useState(null);
    const [ocrResult, setOcrResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleScan = async (selectedFile) => {
        const fileToUpload = selectedFile || file;
        if (!fileToUpload) {
            setError('Please select or capture an image first.');
            return;
        }

        setLoading(true);
        setError('');
        setOcrResult(null);

        const formData = new FormData();
        formData.append('file', fileToUpload);

        try {
            const response = await api.post('/scan/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            // Redirect to results with the event data
            // Expecting backend to return { ..., event_data: { ... } }
            const extractedData = response.data.event_data || response.data.ocr_result;
            navigate('/results', { state: { eventData: extractedData } });

        } catch (err) {
            // Handle API errors properly by displaying messages to the user
            setError(err.response?.data?.detail || 'An error occurred during OCR processing.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
            <h1>Scan Flyer</h1>
            <p>Upload a flyer image or capture one using your camera to extract event details.</p>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '30px' }}>
                <ImageUpload onFileSelect={(f) => { setFile(f); setError(''); }} />
                <CameraCapture onCapture={(f) => { setFile(f); handleScan(f); }} />
            </div>

            {file && !loading && (
                <div style={{ textAlign: 'center', marginBottom: '20px' }}>
                    <button
                        onClick={() => handleScan()}
                        style={{ padding: '12px 30px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '16px' }}
                    >
                        Start Scan
                    </button>
                </div>
            )}

            {loading && (
                <div style={{ textAlign: 'center', padding: '40px' }}>
                    <div className="loader" style={{ marginBottom: '10px' }}>Processing flyer...</div>
                    <p>This may take a few seconds.</p>
                </div>
            )}

            {error && (
                <div style={{ padding: '15px', backgroundColor: '#f8d7da', color: '#721c24', borderRadius: '4px', marginBottom: '20px' }}>
                    <strong>Error:</strong> {error}
                </div>
            )}

            {ocrResult && (
                <div style={{ marginTop: '30px', padding: '20px', border: '1px solid #007bff', borderRadius: '8px', backgroundColor: '#f0f7ff' }}>
                    <h3>OCR Results</h3>
                    <p><strong>Raw Text:</strong></p>
                    <pre style={{ whiteSpace: 'pre-wrap', backgroundColor: '#eee', padding: '10px', borderRadius: '4px' }}>
                        {ocrResult.raw_text}
                    </pre>
                    <div style={{ marginTop: '10px' }}>
                        <p><strong>Word Count:</strong> {ocrResult.word_count}</p>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Scan;
