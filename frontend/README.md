# AI Chat App - Frontend

A modern React TypeScript chat application with authentication and AI conversation management.

## Features

- **Authentication**: Login and signup with email/password
- **Chat Interface**: Real-time chat with AI models
- **Model Selection**: Choose between different AI models and tools
- **Conversation Management**: Create, view, and delete conversations
- **Responsive Design**: Works on desktop and mobile devices
- **Modern UI**: Built with Ant Design components

## Tech Stack

- React 18 with TypeScript
- Ant Design for UI components
- React Router for navigation
- Axios for API calls
- React Context for state management

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- Backend API running on `http://localhost:8000`

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
echo "REACT_APP_API_BASE_URL=http://localhost:8000/api/v1" > .env
```

3. Start the development server:
```bash
npm start
```

The app will open at `http://localhost:3000`.

### Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

## Project Structure

```
src/
├── api/              # API service layer
├── components/       # Reusable components
│   ├── Auth/        # Authentication components
│   ├── Chat/        # Chat interface components
│   └── Sidebar/     # Conversation sidebar
├── contexts/         # React Context providers
├── pages/           # Page components
├── types/           # TypeScript type definitions
└── App.tsx          # Main app component
```

## API Integration

The frontend integrates with the FastAPI backend through the following endpoints:

- **Authentication**: `/auth/login`, `/auth/register`, `/auth/me`
- **Chat**: `/chat/send`, `/chat/regenerate`, `/chat/models`
- **Conversations**: `/conversations/`, `/conversations/{id}/messages`

## Environment Variables

- `REACT_APP_API_BASE_URL` - Backend API base URL (default: `http://localhost:8000/api/v1`)

## Usage

1. **Sign Up/Login**: Create an account or login with existing credentials
2. **Start Chatting**: Click "New Chat" to start a conversation
3. **Select Model**: Choose an AI model from the dropdown
4. **Send Messages**: Type your message and press Enter or click Send
5. **Manage Conversations**: View, switch between, or delete conversations from the sidebar

## Features in Detail

### Authentication
- Secure JWT-based authentication
- Persistent login state
- Protected routes

### Chat Interface
- Real-time message display
- Message copying and regeneration
- Model selection (AI models and internet search)
- Auto-scroll to latest messages
- Responsive message bubbles

### Conversation Management
- Sidebar with conversation list
- Create new conversations
- Delete conversations with confirmation
- Auto-generated conversation titles
- Conversation timestamps

### Responsive Design
- Mobile-friendly sidebar toggle
- Responsive message layout
- Touch-friendly interface
- Custom scrollbars

## Troubleshooting

### Common Issues

1. **API Connection Error**: Ensure the backend is running on `http://localhost:8000`
2. **CORS Issues**: Backend should have CORS configured for `http://localhost:3000`
3. **Authentication Issues**: Check if JWT tokens are properly stored in localStorage

### Development Tips

- Use browser dev tools to inspect network requests
- Check console for any JavaScript errors
- Verify environment variables are loaded correctly
- Ensure backend API is accessible and returning expected responses