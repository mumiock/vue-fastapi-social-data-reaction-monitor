# Social Network Data Processor API

A FastAPI application for processing social network reaction files in real-time with WebSocket support and Redis for event distribution.

## Overview

This application processes social media reaction files in different formats (v1 and v2) and maintains an aggregated database of all reactions. It features real-time data streaming via WebSockets, allowing clients to receive immediate updates when new reaction data is processed.

## Features

- Process v1 and v2 format files through REST API endpoints
- Real-time data updates via WebSocket connections
- Redis pub/sub for event distribution across multiple instances
- Comprehensive REST API for data retrieval and management
- In-memory event storage with historical data tracking
- CORS support for cross-origin requests
- Swagger UI documentation

## Architecture

The application consists of the following components:

- **FastAPI Backend**: Handles HTTP and WebSocket requests
- **Redis**: Used for pub/sub messaging between instances
- **WebSocket Manager**: Manages client connections and broadcasting
- **In-memory Data Store**: Maintains current event counts and historical data

## Prerequisites

- Python 3.8+
- Redis server running locally (or update Redis host in main.py)

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start Redis server:
```bash
# On Windows, download and run Redis server
# On Linux/Mac:
sudo service redis-server start
```

## Running the Application

Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

The server will start at http://localhost:8000

## API Documentation

Access the Swagger UI documentation at http://localhost:8000/docs

## API Endpoints

### Data Upload

- `POST /upload/v1`: Upload v1 format file (post_id,event_type,count)
- `POST /upload/v2`: Upload v2 format file (multi-line format with post_id on separate line)

### Data Retrieval

- `GET /events`: Get all events
- `GET /events/{post_id}`: Get events for specific post
- `GET /api/posts`: Get all posts with event counts
- `GET /api/posts/{post_id}`: Get detailed post data with historical information

### Data Management

- `POST /api/posts/{post_id}/events`: Add a new event to a post
- `DELETE /api/posts/{post_id}`: Delete all data for a post

### WebSocket Endpoints

- `WS /ws/overview`: Connect for overview updates of all posts
- `WS /ws/details/{post_id}`: Connect for detailed updates about a specific post

## WebSocket Events

The WebSocket connection will receive JSON messages in the following formats:

### Initial Data
```json
{
    "type": "initial",
    "data": {
        "post_id": "uuid",
        "events": {"Like": 10, "Unlike": 5},
        "historical_data": {
            "Like": [{"timestamp": "2023-11-10T12:00:00Z", "count": 2, "total": 10}]
        }
    }
}
```

### Update Data
```json
{
    "type": "update",
    "data": {
        "post_id": "uuid",
        "event_type": "Like",
        "count": 5,
        "total": 15,
        "timestamp": "2023-11-10T12:05:00Z"
    }
}
```

## Redis Channel

Events are published to the 'social_events' channel in Redis with the same JSON format as WebSocket update messages.

## Example Usage

### 1. Upload a file using curl:
```bash
curl -X POST -F "file=@v1_input.csv" http://localhost:8000/upload/v1
```

### 2. Connect to WebSocket (JavaScript):
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/overview');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received update:', data);
};
```

### 3. Connect to specific post updates:
```javascript
const postId = 'b6651d07-6b0d-11e9-8ebb-06bad62f3c64';
const ws = new WebSocket(`ws://localhost:8000/ws/details/${postId}`);
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(`Update for post ${postId}:`, data);
};
```

### 4. Use the REST API (Python with httpx):
```python
import httpx

# Get all events
response = httpx.get('http://localhost:8000/events')
print(response.json())

# Add a new event
new_event = {
    "post_id": "b6651d07-6b0d-11e9-8ebb-06bad62f3c64",
    "event_type": "Like",
    "count": 10,
    "total": 10,
    "timestamp": "2023-11-10T12:00:00Z"
}
response = httpx.post(
    'http://localhost:8000/api/posts/b6651d07-6b0d-11e9-8ebb-06bad62f3c64/events', 
    json=new_event
)
print(response.json())
```

## Development

### Adding New File Formats

To add support for new file formats, extend the FastAPI application with new endpoints and processing logic 