# AI Chat App Backend

A comprehensive FastAPI backend for an AI chat application with Ollama LLM integration, Tavily internet search, PostgreSQL database, JWT authentication, and Langfuse monitoring. The backend supports multiple chat modes including intelligent agent-based responses using LlamaIndex ReAct agents.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)
- [Configuration](#configuration)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

## Features

### Authentication & Authorization
- **User Registration**: Create new user accounts with email and password
- **User Login**: Secure authentication with JWT tokens
- **Token Refresh**: Refresh access tokens without re-authentication
- **User Profile**: Get current authenticated user information
- **JWT Middleware**: Protected routes with Bearer token authentication

### Chat Capabilities
- **Multiple Chat Modes**:
  - **None Mode**: Direct AI responses using Ollama models without any tools
  - **Internet Mode**: Direct internet search via Tavily API, returning search results
  - **Auto Mode**: Intelligent LlamaIndex ReAct agent that automatically decides when to use internet search based on query context
- **Message Regeneration**: Regenerate AI responses for any message in a conversation
- **Model Selection**: Support for multiple Ollama models (llama3.1, llama2, mistral, phi-3, etc.)
- **Conversation History**: Maintains context with last 10 messages for coherent conversations
- **Model Discovery**: List all available Ollama models and tool options

### Conversation Management
- **Full CRUD Operations**: Create, read, update, and delete conversations
- **Pagination**: Efficient pagination for listing conversations and messages
- **Message Management**: List, retrieve, and delete individual messages
- **Conversation Export**: Export conversations in JSON or Markdown format
- **Auto-titling**: Conversations automatically get titles from the first message

### LLM Integration
- **Ollama Integration**: Direct integration with Ollama for local LLM inference
- **Multiple Model Support**: Switch between different Ollama models dynamically
- **Conversation Context**: Maintains conversation history for context-aware responses
- **System Messages**: Support for custom system prompts
- **Token Usage Tracking**: Track prompt and completion tokens for each generation

### Intelligent Agent System
- **LlamaIndex ReAct Agent**: Autonomous agent that decides when to use tools
- **Tool Selection Logic**: Agent analyzes queries to determine if internet search is needed
- **Reasoning Transparency**: Logs agent reasoning steps and tool usage decisions
- **Fallback Mechanism**: Gracefully falls back to direct Ollama if agent fails

### Internet Search
- **Tavily API Integration**: High-quality internet search powered by Tavily
- **Search Result Formatting**: Automatically formats search results for LLM consumption
- **Direct Search Mode**: Get search results directly without LLM processing
- **Search Metadata**: Track search depth, result counts, and query information

### Monitoring & Observability
- **Langfuse Integration**: Comprehensive tracing and monitoring of LLM interactions
- **Session Tracking**: Track entire conversation sessions in Langfuse
- **Trace Logging**: Detailed traces for each LLM interaction
- **Tool Call Logging**: Log all tool calls and their results
- **Agent Reasoning Logs**: Track agent decision-making process
- **Error Tracking**: Log errors with context for debugging
- **Token Usage Metrics**: Monitor token consumption and costs

### Health & Monitoring
- **Comprehensive Health Checks**: Individual health checks for all services
- **Database Health**: Verify PostgreSQL connectivity
- **Ollama Health**: Check Ollama service status and available models
- **Search Service Health**: Verify Tavily API connectivity
- **Langfuse Health**: Check Langfuse service status
- **Aggregated Health**: Single endpoint to check all services at once

### Database & Persistence
- **PostgreSQL Database**: Robust relational database for data persistence
- **SQLAlchemy ORM**: Type-safe database operations
- **Alembic Migrations**: Version-controlled database schema management
- **Relationship Management**: Proper foreign keys and cascading deletes
- **JSON Metadata**: Flexible JSON fields for storing message metadata

## Tech Stack

- **Framework**: FastAPI 0.104.1
- **ASGI Server**: Uvicorn
- **Database**: PostgreSQL with SQLAlchemy 2.0.23 ORM
- **Migrations**: Alembic 1.12.1
- **Authentication**: JWT (python-jose) with bcrypt password hashing
- **LLM**: Ollama (local LLM inference)
- **Agent Framework**: LlamaIndex (ReAct agents)
- **Search**: Tavily API
- **Monitoring**: Langfuse 2.7.3
- **Validation**: Pydantic 2.5.0
- **HTTP Client**: httpx 0.25.2

## Architecture

```
Backend/
├── app/
│   ├── api/                    # API endpoints
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── chat.py            # Chat endpoints (send, regenerate, models)
│   │   ├── conversations.py   # Conversation management endpoints
│   │   └── health.py          # Health check endpoints
│   ├── models/                # SQLAlchemy database models
│   │   ├── user.py            # User model
│   │   ├── conversation.py    # Conversation model
│   │   └── message.py         # Message model
│   ├── schemas/               # Pydantic schemas for request/response validation
│   │   ├── user.py            # User schemas
│   │   ├── conversation.py    # Conversation schemas
│   │   └── chat.py            # Chat request/response schemas
│   ├── services/              # Business logic and external service integrations
│   │   ├── auth_service.py    # Authentication business logic
│   │   ├── ollama_service.py  # Ollama LLM integration
│   │   ├── search_service.py  # Tavily search integration
│   │   ├── langfuse_service.py # Langfuse monitoring integration
│   │   └── llamaindex_service.py # LlamaIndex ReAct agent
│   ├── middleware/            # Custom middleware
│   │   └── auth_middleware.py # JWT authentication middleware
│   ├── utils/                 # Utility functions
│   │   └── security.py        # Password hashing and JWT utilities
│   ├── config.py              # Application configuration (Pydantic Settings)
│   ├── database.py            # Database connection and session management
│   └── main.py                # FastAPI application entry point
├── alembic/                   # Database migrations
│   ├── env.py                 # Alembic environment configuration
│   └── versions/              # Migration versions
├── alembic.ini                # Alembic configuration file
├── requirements.txt           # Python dependencies
└── env.example               # Environment variables template
```

## Prerequisites

- **Python**: 3.9 or higher
- **PostgreSQL**: 12 or higher (running locally or remotely)
- **Ollama**: Latest version installed and running (see [Ollama Installation](https://ollama.ai))
- **Tavily API Key**: (Optional) Get from [Tavily](https://tavily.com) for internet search
- **Langfuse**: (Optional) Running instance or cloud account for monitoring

## Quick Start

### 1. Clone and Navigate

```bash
git clone <repository-url>
cd AI-Chat-app/Backend
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Copy the environment template and configure your settings:

```bash
cp env.example .env
```

Edit `.env` with your configuration:

```env
# Database Configuration
DATABASE_URL=postgresql://chatapp_user:chatapp_password@localhost:5432/chatapp

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama3:latest

# Tavily Search API (Optional - for internet search)
TAVILY_API_KEY=your_tavily_api_key_here

# Langfuse Configuration (Optional - for monitoring)
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key_here
LANGFUSE_SECRET_KEY=your_langfuse_secret_key_here
LANGFUSE_HOST=http://localhost:3000

# JWT Configuration
JWT_SECRET_KEY=your_super_secret_jwt_key_here_change_this_in_production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
ENVIRONMENT=development
DEBUG=true
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
```

### 5. Set Up PostgreSQL Database

Create a PostgreSQL database:

```bash
# Using psql
createdb chatapp
# Or create user and database
psql -U postgres
CREATE USER chatapp_user WITH PASSWORD 'chatapp_password';
CREATE DATABASE chatapp OWNER chatapp_user;
GRANT ALL PRIVILEGES ON DATABASE chatapp TO chatapp_user;
```

### 6. Run Database Migrations

```bash
alembic upgrade head
```

### 7. Start Ollama (if not already running)

```bash
# Install Ollama from https://ollama.ai if not installed
ollama serve

# In another terminal, pull a model
ollama pull llama3:latest
# Or pull other models
ollama pull llama2
ollama pull mistral
ollama pull phi3
```

### 8. Run the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/register` | Register a new user | No |
| POST | `/api/v1/auth/login` | Login and get access token | No |
| GET | `/api/v1/auth/me` | Get current user information | Yes |
| POST | `/api/v1/auth/refresh` | Refresh access token | Yes |

### Chat

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/chat/send` | Send a message and get AI response | Yes |
| POST | `/api/v1/chat/regenerate` | Regenerate an AI response | Yes |
| GET | `/api/v1/chat/models` | Get available Ollama models and tools | Yes |

**Chat Request Body:**
```json
{
  "message": "What are the latest developments in AI?",
  "conversation_id": 1,  // Optional: continue existing conversation
  "tool_selection": "auto",  // "none", "internet", or "auto"
  "model": "llama3:latest"  // Optional: specify Ollama model
}
```

### Conversations

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/conversations/` | List all conversations (paginated) | Yes |
| POST | `/api/v1/conversations/` | Create a new conversation | Yes |
| GET | `/api/v1/conversations/{id}` | Get conversation with all messages | Yes |
| PUT | `/api/v1/conversations/{id}` | Update conversation (e.g., title) | Yes |
| DELETE | `/api/v1/conversations/{id}` | Delete conversation and all messages | Yes |
| GET | `/api/v1/conversations/{id}/messages` | Get conversation messages (paginated) | Yes |
| DELETE | `/api/v1/conversations/{id}/messages/{message_id}` | Delete a specific message | Yes |
| GET | `/api/v1/conversations/{id}/export` | Export conversation (JSON or Markdown) | Yes |

**Query Parameters for Export:**
- `format`: `json` or `markdown` (default: `json`)

### Health Checks

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/health/` | Basic health check | No |
| GET | `/api/v1/health/database` | Database connectivity check | No |
| GET | `/api/v1/health/ollama` | Ollama service health check | No |
| GET | `/api/v1/health/search` | Tavily search service health check | No |
| GET | `/api/v1/health/langfuse` | Langfuse service health check | No |
| GET | `/api/v1/health/all` | Check all services health | No |

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `OLLAMA_BASE_URL` | Ollama service URL | Yes | `http://localhost:11434` |
| `OLLAMA_DEFAULT_MODEL` | Default Ollama model to use | Yes | `llama3:latest` |
| `TAVILY_API_KEY` | Tavily search API key | No* | - |
| `LANGFUSE_PUBLIC_KEY` | Langfuse public key | No* | - |
| `LANGFUSE_SECRET_KEY` | Langfuse secret key | No* | - |
| `LANGFUSE_HOST` | Langfuse host URL | No* | `http://localhost:3000` |
| `JWT_SECRET_KEY` | JWT signing secret | Yes | - |
| `JWT_ALGORITHM` | JWT algorithm | No | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | No | `30` |
| `ENVIRONMENT` | Environment name | No | `development` |
| `DEBUG` | Enable debug mode | No | `true` |
| `CORS_ORIGINS` | Allowed CORS origins (JSON array) | No | `["*"]` |
| `API_V1_PREFIX` | API prefix | No | `/api/v1` |
| `CHAT_MEMORY_BUFFER_SIZE` | Conversation history buffer size | No | `20` |
| `LLAMAINDEX_MAX_ITERATIONS` | Max agent iterations | No | `5` |
| `LLAMAINDEX_VERBOSE` | Enable verbose agent logging | No | `true` |

*Required only if using the respective feature (internet search or Langfuse monitoring)

### Supported Ollama Models

The backend supports any Ollama model. Common models include:
- `llama3:latest` - Latest Llama 3 model (recommended)
- `llama3.1:latest` - Llama 3.1 model
- `llama2` - Llama 2 model
- `mistral` - Mistral model
- `phi3` - Phi-3 lightweight model

Pull models using: `ollama pull <model_name>`

### Chat Modes Explained

1. **None Mode** (`tool_selection: "none"`):
   - Direct AI response using Ollama
   - No internet search
   - Fastest response time
   - Best for general questions and conversations

2. **Internet Mode** (`tool_selection: "internet"`):
   - Direct internet search via Tavily
   - Returns formatted search results
   - No LLM processing of search results
   - Best for getting current information quickly

3. **Auto Mode** (`tool_selection: "auto"`):
   - LlamaIndex ReAct agent analyzes the query
   - Agent decides whether to use internet search
   - Combines search results with LLM reasoning
   - Best for complex queries requiring both knowledge and reasoning

## Development

### Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migration:
```bash
alembic downgrade -1
```
### Code Structure Guidelines

- **API Routes** (`app/api/`): Handle HTTP requests, validate input, call services
- **Services** (`app/services/`): Business logic and external service integrations
- **Models** (`app/models/`): SQLAlchemy database models
- **Schemas** (`app/schemas/`): Pydantic models for request/response validation
- **Middleware** (`app/middleware/`): Custom middleware (auth, logging, etc.)
- **Utils** (`app/utils/`): Reusable utility functions

### Adding New Features

1. Create database models in `app/models/`
2. Create Pydantic schemas in `app/schemas/`
3. Implement business logic in `app/services/`
4. Create API endpoints in `app/api/`
5. Register routes in `app/main.py`
6. Create and run migrations if database changes are needed

## Troubleshooting

### Common Issues

#### 1. Ollama Connection Failed

**Error**: `Cannot connect to Ollama at http://localhost:11434`

**Solutions**:
- Ensure Ollama is running: `ollama serve`
- Check if Ollama is accessible: `curl http://localhost:11434/api/tags`
- Verify `OLLAMA_BASE_URL` in `.env` matches your Ollama instance
- Ensure the model is pulled: `ollama pull llama3:latest`

#### 2. Database Connection Error

**Error**: `Could not connect to database`

**Solutions**:
- Verify PostgreSQL is running: `pg_isready` or `psql -U postgres`
- Check `DATABASE_URL` in `.env` is correct
- Ensure database exists: `psql -U postgres -l`
- Verify user has proper permissions

#### 3. Tavily Search Not Working

**Error**: `Tavily API key not configured` or `Invalid Tavily API key`

**Solutions**:
- Verify `TAVILY_API_KEY` is set in `.env`
- Get a valid API key from [Tavily](https://tavily.com)
- Check API quota limits
- Verify internet connectivity

#### 4. Langfuse Traces Not Appearing

**Error**: `Langfuse connection failed` or traces not showing in UI

**Solutions**:
- Verify Langfuse credentials in `.env`
- Check Langfuse service is running (if self-hosted)
- Verify `LANGFUSE_HOST` URL is correct
- Check network connectivity to Langfuse instance

#### 5. LlamaIndex Agent Fails

**Error**: `Auto mode failed` or agent errors

**Solutions**:
- Ensure Ollama supports `/api/chat` endpoint (update Ollama if needed)
- Verify model is loaded: `ollama list`
- Check if Tavily API key is configured (required for agent tools)
- Review logs for specific error messages
- Agent will automatically fallback to direct Ollama if it fails

#### 6. Import Errors or Missing Dependencies

**Error**: `ModuleNotFoundError` or import errors

**Solutions**:
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.9+)

#### 7. CORS Errors

**Error**: CORS policy errors in browser

**Solutions**:
- Update `CORS_ORIGINS` in `.env` to include your frontend URL
- Format as JSON array: `["http://localhost:3000", "http://localhost:8080"]`
- Restart the server after changing CORS settings

### Debugging Tips

1. **Enable Debug Mode**: Set `DEBUG=true` in `.env` for detailed error messages
2. **Check Logs**: Review application logs for detailed error information
3. **Health Checks**: Use `/api/v1/health/all` to check all service statuses
4. **Test Individual Services**: Use specific health check endpoints to isolate issues
5. **Database Queries**: Use `echo=True` in SQLAlchemy engine (already enabled in debug mode) to see SQL queries

### Getting Help

- Check the [FastAPI Documentation](https://fastapi.tiangolo.com/)
- Review [Ollama Documentation](https://github.com/ollama/ollama)
- Consult [LlamaIndex Documentation](https://docs.llamaindex.ai/)
- Check [Tavily API Documentation](https://docs.tavily.com/)
- Review [Langfuse Documentation](https://langfuse.com/docs)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request
