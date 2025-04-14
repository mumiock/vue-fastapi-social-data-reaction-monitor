# Social Network Monitor - Client Application

A Vue.js application for monitoring and visualizing social network reactions in real-time. This client application connects to the FastAPI backend to display and manage social media reaction data.

## Overview

This client application provides a user-friendly interface for viewing social network post reactions and their historical trends. It features real-time updates via WebSockets, data visualization with Plotly.js, and a responsive design using Bootstrap.

## Features

- **Real-time Dashboard**: View all social network posts with their reaction counts
- **Post Details View**: Examine detailed statistics and historical trends for specific posts
- **Live Updates**: Receive and display updates in real-time via WebSocket connection
- **Interactive Charts**: Visualize reaction trends with dynamic charts
- **Responsive Design**: Fully responsive layout that works on desktop and mobile devices
- **Search Functionality**: Filter and find specific posts by ID

## Tech Stack

- **Vue.js 3**: Front-end framework
- **Vuex**: State management
- **Vue Router**: Navigation and routing
- **Bootstrap 5**: UI components and responsive design
- **Axios**: HTTP client for API requests
- **Plotly.js**: Data visualization and charting
- **WebSockets**: Real-time communication with the server

## Prerequisites

- Node.js 14+
- npm or yarn
- FastAPI backend running (see the [backend README](../fastapi/README.md))

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/social-network-processor.git
cd social-network-processor/client
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file in the client directory with the following content:
```
VUE_APP_API_URL=http://localhost:8000
VUE_APP_WS_URL=ws://localhost:8000
```

## Running the Application

Start the development server:
```bash
npm run serve
```

The application will be available at http://localhost:8080

### Building for Production

To create a production build:
```bash
npm run build
```

The compiled files will be available in the `dist` directory.

## Application Structure

- `src/views/`: Main page components (HomeView, PostDetailsView)
- `src/components/`: Reusable Vue components
- `src/services/`: API and WebSocket service modules
- `src/store/`: Vuex state management store
- `src/router/`: Vue Router configuration

## WebSocket Integration

The application maintains two types of WebSocket connections:
1. An overview connection for updates to all posts
2. A details connection for specific post updates

When new data arrives via WebSockets, the Vuex store updates accordingly, triggering reactive updates in the UI.

## API Integration

The application communicates with the FastAPI backend using the following endpoints:

- `GET /api/posts`: Get all posts
- `GET /api/posts/{post_id}`: Get detailed post data
- `POST /api/posts/{post_id}/events`: Add an event to a post
- `DELETE /api/posts/{post_id}`: Delete a post

## Customization

### Environment Variables

- `VUE_APP_API_URL`: Backend API URL (default: http://localhost:8000)
- `VUE_APP_WS_URL`: WebSocket URL (default: ws://localhost:8000)

## Development

### Code Style and Linting

The project uses ESLint for code quality. To run the linter:
```bash
npm run lint
```

### Adding New Features

To add new visualization types or dashboard widgets:
1. Create new components in the `src/components` directory
2. Add any required API calls to the `src/services/api.js` file
3. Update the Vuex store as needed to manage new data
4. Integrate the components into the appropriate views

## Connecting to a Custom Backend

To connect to a different backend:
1. Update the `.env` file with the appropriate API and WebSocket URLs
2. Ensure the backend follows the same API structure or update the API service to match

## License

This project is licensed under the MIT License - see the LICENSE file for details. 