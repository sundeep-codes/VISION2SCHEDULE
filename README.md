# Vision2Schedule

Vision2Schedule is an intelligent application that allows users to upload event posters or flyers, automatically extracts event details using OCR (Optical Character Recognition), and seamlessly integrates them into Google Calendar. It also helps users explore nearby events within a 5km radius and download event details as ICS files.

## 🚀 Key Features

- **Poster Upload & Scan**: Effortlessly upload event flyers for scanning.
- **OCR Extraction**: Automated extraction of event title, date, time, and location.
- **Confidence Score**: Get a confidence rating on the accuracy of the extracted details.
- **Save & History**: View past scanned events in your personal history dashboard.
- **Nearby Events**: Discover relevant events happening within a 5km radius of the scanned location.
- **Google Calendar Sync**: Add extracted events straight to your Google Calendar with one click.
- **ICS Download**: Export event details as an `.ics` file for other calendar clients.

## 💻 Tech Stack

**Frontend:**
- React 19
- Vite
- React Router DOM
- Axios

**Backend:**
- Python 3
- FastAPI
- SQLAlchemy (Database ORM)
- Uvicorn (ASGI server)
- JWT (Authentication)

## 📁 Project Structure

```text
Vision2Schedule/
├── backend/                  # Root python backend files
│   ├── main.py               # FastAPI application entry point
│   ├── auth.py               # User authentication logic
│   ├── ocr.py / extract.py   # OCR processing and data extraction
│   ├── events.py / calendar.py # Google Calendar & ICS integrations
│   ├── scan_router.py        # API routes for scanning flyers
│   ├── nearby.py / nearby_router.py # Nearby events logic
│   ├── database.py / models.py # Database configuration and models
│   └── security.py           # JWT and security utilities
└── frontend/                 # React frontend application
    ├── src/
    │   ├── components/       # Reusable React components (Navbar, etc.)
    │   └── pages/            # Page-level components (Scan, History, etc.)
    ├── package.json          # Frontend dependencies
    └── vite.config.js        # Vite configuration
```

## 🛠️ How to Run Locally

### Backend Setup

1. **Navigate to the project directory:**
   ```bash
   cd Vision2Schedule
   ```

2. **Create and activate a virtual environment (Optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(If `requirements.txt` is missing, manually install `fastapi`, `uvicorn`, `sqlalchemy`, `python-jose`, etc.)*

4. **Run the FastAPI server:**
   ```bash
   uvicorn main:app --reload
   ```
   The backend will be running at `http://localhost:8000`. API documentation is available at `http://localhost:8000/docs`.

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```
   The frontend will be running at `http://localhost:5173`.

## 🔐 Required Environment Variables

Create `.env` files for both frontend and backend based on the following keys.

**Backend (`.env` in root):**
```env
DATABASE_URL=sqlite:///./v2s.db
JWT_SECRET_KEY=your_super_secret_jwt_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
OCR_SPACE_API_KEY=your_ocr_space_api_key
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
EVENTBRITE_API_TOKEN=your_eventbrite_api_token
```

**Frontend (`frontend/.env`):**
```env
VITE_API_URL=http://localhost:8000
```

## 🔑 API Keys Required

To fully utilize Vision2Schedule, you will need the following API keys:
1. **OCR.Space API Key** - For extracting text from uploaded images.
2. **Google Maps API Key** - For calculating nearby events with location coordinates.
3. **Eventbrite API Token** - For fetching nearby events.
4. **Google Cloud Console Credentials (OAuth Client ID & Secret)** - Required for Google Calendar Sync integration.

## 📸 Screenshots

*(Add your screenshots here)*

![Scan Page Placeholder](docs/screenshots/scan-page.png)
*Scanning an event poster.*

![History Page Placeholder](docs/screenshots/history-page.png)
*Viewing the history of scanned events.*

## 🔮 Future Improvements

- **Enhanced Error Handling**: Better fallbacks and suggestions for low-quality poster uploads.
- **More Calendar Integrations**: Support for Outlook Calendar, Apple Calendar, and Yahoo Calendar native auth.
- **Social Sharing**: Ability to share scanned events directly to social media or messaging platforms.
- **Advanced Event Discovery**: Filter nearby events by tags or categories.
