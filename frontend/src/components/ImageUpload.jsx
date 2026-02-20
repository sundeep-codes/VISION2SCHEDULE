import React, { useState } from 'react';

const ImageUpload = ({ onFileSelect }) => {
    const [preview, setPreview] = useState(null);

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            onFileSelect(file);
            const reader = new FileReader();
            reader.onloadend = () => {
                setPreview(reader.result);
            };
            reader.readAsDataURL(file);
        }
    };

    return (
        <div style={{ padding: '20px', border: '2px dashed #ccc', borderRadius: '10px', textAlign: 'center', marginBottom: '20px' }}>
            <h3>Upload Flyer</h3>
            <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                style={{ marginBottom: '10px' }}
            />
            {preview && (
                <div style={{ marginTop: '10px' }}>
                    <img src={preview} alt="Flyer Preview" style={{ maxWidth: '100%', maxHeight: '300px', borderRadius: '8px' }} />
                </div>
            )}
        </div>
    );
};

export default ImageUpload;
