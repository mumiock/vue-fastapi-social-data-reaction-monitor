# Social Network Reaction Processor

A full-stack application for processing and visualizing social network reaction data in real-time.

## Project Structure

This repository contains two main components:

- **[FastAPI Backend](./fastapi/)**: Processes social network reaction files and provides real-time data via WebSockets
- **[Vue.js Frontend](./client/)**: Visualizes the reaction data with interactive charts and real-time updates

## Features

- 📊 Process social reaction files in multiple formats (v1 and v2)
- ⚡ Real-time data updates via WebSockets
- 📈 Interactive visualization of reaction trends
- 🔍 Search and filter capabilities for finding specific posts
- 🧰 RESTful API for data management
- 📱 Responsive design that works on all devices

## Tech Stack

- **Backend**: FastAPI, Redis, WebSockets, Python
- **Frontend**: Vue.js 3, Vuex, Vue Router, Bootstrap 5, Plotly.js

## Quick Start

### Backend Setup

```bash
# Navigate to backend directory
cd fastapi

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start Redis server (required)
# On Windows, download and run Redis server
# On Linux/Mac: sudo service redis-server start

# Start the FastAPI server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd client

# Install dependencies
npm install

# Start development server
npm run serve
```

Visit:
- Backend: http://localhost:8000
- Frontend: http://localhost:8080
- API Documentation: http://localhost:8000/docs

## Documentation

For detailed documentation, please refer to:
- [FastAPI Backend Documentation](./fastapi/README.md)
- [Vue.js Frontend Documentation](./client/README.md)

## License

This project is licensed under the MIT License. 