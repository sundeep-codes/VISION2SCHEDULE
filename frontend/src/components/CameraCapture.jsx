import React, { useRef, useState, useEffect } from 'react';

const CameraCapture = ({ onCapture }) => {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const [isStreaming, setIsStreaming] = useState(false);
    const [error, setError] = useState(null);

    const startCamera = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                setIsStreaming(true);
                setError(null);
            }
        } catch (err) {
            setError("Unable to access camera. Please check permissions.");
            console.error(err);
        }
    };

    const stopCamera = () => {
        if (videoRef.current && videoRef.current.srcObject) {
            const tracks = videoRef.current.srcObject.getTracks();
            tracks.forEach(track => track.stop());
            setIsStreaming(false);
        }
    };

    const captureImage = () => {
        if (canvasRef.current && videoRef.current) {
            const context = canvasRef.current.getContext('2d');
            canvasRef.current.width = videoRef.current.videoWidth;
            canvasRef.current.height = videoRef.current.videoHeight;
            context.drawImage(videoRef.current, 0, 0, canvasRef.current.width, canvasRef.current.height);

            canvasRef.current.toBlob((blob) => {
                if (blob) {
                    const file = new File([blob], "camera_capture.jpg", { type: "image/jpeg" });
                    onCapture(file);
                    stopCamera();
                }
            }, 'image/jpeg');
        }
    };

    useEffect(() => {
        return () => stopCamera();
    }, []);

    return (
        <div style={{ padding: '20px', border: '1px solid #ccc', borderRadius: '10px', textAlign: 'center', marginBottom: '20px' }}>
            <h3>Camera Capture</h3>
            {error && <p style={{ color: 'red' }}>{error}</p>}

            {!isStreaming ? (
                <button onClick={startCamera} style={{ padding: '10px 20px', cursor: 'pointer' }}>Start Camera</button>
            ) : (
                <div>
                    <video ref={videoRef} autoPlay playsInline style={{ width: '100%', maxWidth: '400px', borderRadius: '8px' }} />
                    <div style={{ marginTop: '10px' }}>
                        <button onClick={captureImage} style={{ padding: '10px 20px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', marginRight: '10px' }}>Capture</button>
                        <button onClick={stopCamera} style={{ padding: '10px 20px', cursor: 'pointer' }}>Cancel</button>
                    </div>
                </div>
            )}
            <canvas ref={canvasRef} style={{ display: 'none' }} />
        </div>
    );
};

export default CameraCapture;
