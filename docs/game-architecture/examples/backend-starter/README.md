# Game Backend Starter

A complete Python/FastAPI backend starter for game development with user authentication, character management, and real-time chat.

## Features

- FastAPI with automatic API documentation
- SQLAlchemy ORM with PostgreSQL/SQLite support
- JWT authentication
- WebSocket support for real-time features
- Comprehensive testing setup
- Docker support

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up database
python scripts/setup_database.py

# Run development server
uvicorn main:app --reload

# API documentation available at: http://localhost:8000/docs
```

## Project Structure

```
backend-starter/
├── api/                    # API endpoints
│   ├── auth.py            # Authentication routes
│   ├── characters.py      # Character management
│   ├── chat.py           # Chat functionality
│   └── items.py          # Item/inventory management
├── models/                # Database models
│   ├── user.py           # User model
│   ├── character.py      # Character model
│   └── chat.py           # Chat models
├── services/              # Business logic
│   ├── auth_service.py   # Authentication logic
│   ├── character_service.py # Character logic
│   └── chat_service.py   # Chat logic
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── conftest.py       # Test configuration
├── main.py               # FastAPI application
├── database.py           # Database configuration
├── requirements.txt      # Python dependencies
└── Dockerfile           # Docker configuration
```

## Configuration

Copy `.env.example` to `.env` and configure:

```env
DATABASE_URL=postgresql://user:password@localhost/gamedb
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

### Characters
- `POST /api/characters` - Create character
- `GET /api/characters` - List user characters
- `GET /api/characters/{id}` - Get character details
- `PUT /api/characters/{id}` - Update character

### Chat
- `GET /api/chat/channels` - List channels
- `GET /api/chat/channels/{id}/messages` - Get messages
- `POST /api/chat/channels/{id}/messages` - Send message
- `WS /api/chat/ws/{channel_id}` - WebSocket connection

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/unit/test_character_service.py
```

## Deployment

### Docker
```bash
docker build -t game-backend .
docker run -p 8000:8000 game-backend
```

### Docker Compose
```bash
docker-compose up -d
```

## Development

### Adding New Features

1. Create model in `models/`
2. Create service in `services/`
3. Create API routes in `api/`
4. Add tests in `tests/`
5. Update documentation

### Database Migrations

```bash
# Generate migration
alembic revision --autogenerate -m "Add new feature"

# Apply migration
alembic upgrade head
```