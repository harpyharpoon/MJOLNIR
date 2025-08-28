# Incremental Migration Plan

## Overview

This document provides a step-by-step migration plan to convert an existing game prototype (monolithic or in another language) into a Python backend with a JavaScript frontend. The plan prioritizes minimal downtime, incremental refactoring, and identifies potential pitfalls.

## Migration Strategy

### Phase 0: Preparation and Assessment (1-2 weeks)

#### Week 1: Analysis
- [ ] **Code Audit**: Document all existing functionality
- [ ] **Dependency Mapping**: Identify all external dependencies
- [ ] **Data Model Analysis**: Document current data structures
- [ ] **User Flow Documentation**: Map all user interactions
- [ ] **Performance Baseline**: Establish current performance metrics

#### Week 2: Planning
- [ ] **Architecture Design**: Create target architecture diagrams
- [ ] **API Design**: Design REST API endpoints (see [API Design Guide](./02-api-design.md))
- [ ] **Migration Order**: Prioritize components for migration
- [ ] **Risk Assessment**: Identify potential blockers and mitigation strategies
- [ ] **Testing Strategy**: Plan testing approach for each phase

### Phase 1: Infrastructure Setup (1 week)

#### Backend Infrastructure
```bash
# Create project structure
mkdir game-backend
cd game-backend

# Initialize Python project
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

# Install core dependencies
pip install fastapi uvicorn sqlalchemy alembic pytest

# Create basic structure
mkdir -p {api,models,services,tests,migrations}
touch {api,models,services,tests}/__init__.py
```

#### Frontend Infrastructure
```bash
# Create frontend project
mkdir game-frontend
cd game-frontend

# Initialize JavaScript project (if using build tools)
npm init -y
npm install axios socket.io-client

# Or create simple HTML structure
mkdir -p {js,css,components}
touch index.html js/main.js css/style.css
```

#### Database Setup
```python
# backend/models/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./game.db"  # Start with SQLite
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Phase 2: Data Layer Migration (1-2 weeks)

#### Step 1: Database Schema Design
```python
# backend/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# backend/models/character.py
class Character(Base):
    __tablename__ = "characters"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, index=True)
    character_class = Column(String)
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    # Add other attributes...
```

#### Step 2: Data Migration Script
```python
# scripts/migrate_data.py
import json
import sqlite3
from sqlalchemy.orm import Session
from backend.models import User, Character
from backend.models.database import engine, get_db

def migrate_existing_data():
    """Migrate data from existing system"""
    # Example: Migrate from JSON files
    with open('old_data/users.json', 'r') as f:
        old_users = json.load(f)
    
    db = SessionLocal()
    try:
        for old_user in old_users:
            new_user = User(
                username=old_user['username'],
                email=old_user.get('email', f"{old_user['username']}@game.com"),
                hashed_password=hash_password(old_user['password'])
            )
            db.add(new_user)
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    # Run migration
    Base.metadata.create_all(bind=engine)
    migrate_existing_data()
```

### Phase 3: Backend API Development (2-3 weeks)

#### Week 1: Core APIs
```python
# backend/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .models.database import get_db
from .api import auth, characters, items

app = FastAPI(title="Game API", version="1.0.0")

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(characters.router, prefix="/api/characters", tags=["characters"])
app.include_router(items.router, prefix="/api/items", tags=["items"])

@app.get("/")
async def root():
    return {"message": "Game API is running"}

# Run with: uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

#### Authentication Implementation
```python
# backend/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..models.database import get_db
from ..services.auth_service import AuthService

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/register")
async def register(
    username: str,
    email: str,
    password: str,
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    try:
        user = auth_service.create_user(username, email, password)
        return {"message": "User created successfully", "user_id": user.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token = auth_service.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
```

#### Character API Implementation
```python
# backend/api/characters.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..models.database import get_db
from ..services.character_service import CharacterService
from ..services.auth_service import get_current_user
from ..schemas.character import CharacterCreate, CharacterResponse

router = APIRouter()

@router.post("/", response_model=CharacterResponse)
async def create_character(
    character_data: CharacterCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = CharacterService(db)
    character = service.create_character(current_user.id, character_data.dict())
    return character

@router.get("/", response_model=List[CharacterResponse])
async def get_characters(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = CharacterService(db)
    return service.get_user_characters(current_user.id)
```

### Phase 4: Frontend Development (2-3 weeks)

#### Basic HTML Structure
```html
<!-- frontend/index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Game Client</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div id="app">
        <div id="auth-section" class="hidden">
            <!-- Login/Register forms -->
        </div>
        <div id="game-section" class="hidden">
            <nav id="game-nav">
                <button id="characters-tab">Characters</button>
                <button id="inventory-tab">Inventory</button>
                <button id="quests-tab">Quests</button>
                <button id="chat-tab">Chat</button>
            </nav>
            <main id="game-content">
                <!-- Dynamic content -->
            </main>
        </div>
    </div>
    
    <script src="js/api-client.js"></script>
    <script src="js/auth.js"></script>
    <script src="js/characters.js"></script>
    <script src="js/main.js"></script>
</body>
</html>
```

#### API Client Implementation
```javascript
// frontend/js/api-client.js
class GameAPIClient {
    constructor(baseURL = 'http://localhost:8000/api') {
        this.baseURL = baseURL;
        this.token = localStorage.getItem('authToken');
    }
    
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };
        
        if (this.token) {
            config.headers.Authorization = `Bearer ${this.token}`;
        }
        
        if (config.body && typeof config.body === 'object') {
            config.body = JSON.stringify(config.body);
        }
        
        const response = await fetch(url, config);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'API request failed');
        }
        
        return response.json();
    }
    
    // Authentication methods
    async login(username, password) {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        
        const response = await this.request('/auth/login', {
            method: 'POST',
            body: formData,
            headers: {} // Let browser set Content-Type for FormData
        });
        
        this.token = response.access_token;
        localStorage.setItem('authToken', this.token);
        return response;
    }
    
    async register(username, email, password) {
        return this.request('/auth/register', {
            method: 'POST',
            body: { username, email, password }
        });
    }
    
    // Character methods
    async getCharacters() {
        return this.request('/characters');
    }
    
    async createCharacter(characterData) {
        return this.request('/characters', {
            method: 'POST',
            body: characterData
        });
    }
}
```

### Phase 5: Feature Migration (3-4 weeks)

#### Week 1: Character System
- [ ] Migrate character creation logic
- [ ] Implement character management UI
- [ ] Add character selection functionality
- [ ] Test character persistence

#### Week 2: Inventory System
- [ ] Migrate item data models
- [ ] Implement inventory API endpoints
- [ ] Create inventory management UI
- [ ] Add item interaction features

#### Week 3: Quest System
- [ ] Migrate quest logic
- [ ] Implement quest API endpoints
- [ ] Create quest board UI
- [ ] Add quest progression tracking

#### Week 4: Chat System
- [ ] Implement WebSocket communication
- [ ] Migrate chat functionality
- [ ] Create chat UI components
- [ ] Add real-time messaging

### Phase 6: Real-time Features (1-2 weeks)

#### WebSocket Implementation
```python
# backend/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.user_connections[user_id] = websocket
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        self.active_connections.remove(websocket)
        if user_id in self.user_connections:
            del self.user_connections[user_id]
    
    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.user_connections:
            await self.user_connections[user_id].send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data['type'] == 'chat_message':
                # Broadcast chat message
                await manager.broadcast(data)
            elif message_data['type'] == 'game_update':
                # Handle game state updates
                await handle_game_update(message_data)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
```

### Phase 7: Testing and Optimization (1-2 weeks)

#### Backend Testing
```python
# tests/test_character_api.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_create_character():
    # Create user first
    response = client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass"
    })
    assert response.status_code == 200
    
    # Login
    response = client.post("/api/auth/login", data={
        "username": "testuser",
        "password": "testpass"
    })
    token = response.json()["access_token"]
    
    # Create character
    response = client.post("/api/characters", 
        json={"name": "TestChar", "class": "warrior"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "TestChar"
```

#### Frontend Testing
```javascript
// tests/api-client.test.js
describe('GameAPIClient', () => {
    let client;
    
    beforeEach(() => {
        client = new GameAPIClient('http://localhost:8000/api');
    });
    
    test('should login successfully', async () => {
        // Mock fetch
        global.fetch = jest.fn(() =>
            Promise.resolve({
                ok: true,
                json: () => Promise.resolve({
                    access_token: 'test-token',
                    token_type: 'bearer'
                })
            })
        );
        
        const response = await client.login('testuser', 'testpass');
        expect(response.access_token).toBe('test-token');
        expect(client.token).toBe('test-token');
    });
});
```

### Phase 8: Deployment and Go-Live (1 week)

#### Production Setup
```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/gamedb
    depends_on:
      - db
  
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
  
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: gamedb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Risk Mitigation

### Common Pitfalls and Solutions

#### 1. Data Loss During Migration
**Risk**: Losing user data during database migration
**Mitigation**:
- Always backup before migration
- Test migration on copy of production data
- Implement rollback procedures
- Use staged migration approach

#### 2. Authentication Compatibility
**Risk**: Users unable to log in after migration
**Mitigation**:
- Maintain password compatibility
- Implement password migration on first login
- Provide account recovery mechanism

#### 3. Performance Degradation
**Risk**: New architecture being slower than original
**Mitigation**:
- Establish performance baselines
- Load test each component
- Implement caching strategies
- Monitor performance continuously

#### 4. Feature Parity Issues
**Risk**: Missing features in new system
**Mitigation**:
- Complete feature audit before starting
- Implement feature flags for gradual rollout
- Maintain old system in parallel initially

### Rollback Strategy

#### Immediate Rollback (< 1 hour)
```bash
# Switch DNS back to old system
# Restore database from backup
# Notify users of temporary issue
```

#### Data Sync Rollback (< 24 hours)
```bash
# Export any new data from new system
# Restore old system
# Import critical new data
# Implement data reconciliation
```

## Success Metrics

### Technical Metrics
- [ ] API response time < 200ms for 95th percentile
- [ ] Zero data loss during migration
- [ ] 99.9% uptime during migration period
- [ ] All existing features working in new system

### User Experience Metrics
- [ ] User satisfaction score maintained or improved
- [ ] Login success rate > 99%
- [ ] Feature usage patterns similar to old system
- [ ] Support ticket volume not increased

### Business Metrics
- [ ] No revenue impact during migration
- [ ] User retention rate maintained
- [ ] New user registration rate maintained or improved

## Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| 0. Preparation | 1-2 weeks | Architecture plan, risk assessment |
| 1. Infrastructure | 1 week | Dev environment, CI/CD |
| 2. Data Layer | 1-2 weeks | Database schema, migration scripts |
| 3. Backend API | 2-3 weeks | Core APIs, authentication |
| 4. Frontend | 2-3 weeks | UI components, API integration |
| 5. Feature Migration | 3-4 weeks | Complete feature set |
| 6. Real-time Features | 1-2 weeks | WebSocket, live updates |
| 7. Testing | 1-2 weeks | Comprehensive testing |
| 8. Deployment | 1 week | Production deployment |

**Total Timeline: 12-20 weeks**

## Next Steps

1. Review [Chat Broadcasting Example](./05-chat-example.md) for practical implementation
2. Check [Testing Strategy](./06-testing-integration.md) for comprehensive testing approach
3. Start with Phase 0 preparation and customize timeline based on your specific needs