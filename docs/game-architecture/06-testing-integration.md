# Testing and Integration Strategy

## Overview

This document outlines a comprehensive testing strategy and suggests tools for ensuring reliable integration between Python backend and JavaScript frontend. It covers unit testing, API contract validation, end-to-end UI testing, and integration testing approaches.

## Testing Pyramid

```
                    ▲
                   /|\
                  / | \
                 /  |  \
                /   |   \
               /    |    \
              /     |     \
             /      |      \
            /       |       \
           /        |        \
          /         |         \
         /_______E2E_______\     - UI Tests, Integration Tests
        /___________________\    - API Tests, Contract Tests  
       /____________________\   - Unit Tests, Component Tests
```

### Test Types Distribution
- **70%** Unit Tests (Fast, isolated, many)
- **20%** Integration/API Tests (Medium speed, fewer)
- **10%** End-to-End Tests (Slow, complex, critical paths only)

## Backend Testing Strategy

### 1. Unit Testing with pytest

#### Test Structure
```
backend/tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── unit/
│   ├── test_auth_service.py
│   ├── test_character_service.py
│   ├── test_chat_service.py
│   └── test_quest_service.py
├── integration/
│   ├── test_api_endpoints.py
│   ├── test_database_operations.py
│   └── test_websocket_connections.py
└── e2e/
    └── test_complete_workflows.py
```

#### Test Configuration
```python
# backend/tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from backend.main import app
from backend.models.database import Base, get_db
from backend.services.auth_service import AuthService

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with test database"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    auth_service = AuthService(db_session)
    user = auth_service.create_user(
        username="testuser",
        email="test@example.com",
        password="testpassword"
    )
    return user

@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for test requests"""
    response = client.post("/api/auth/login", data={
        "username": "testuser",
        "password": "testpassword"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

#### Unit Test Examples
```python
# backend/tests/unit/test_character_service.py
import pytest
from backend.services.character_service import CharacterService, CharacterError
from backend.models.character import Character

class TestCharacterService:
    
    def test_create_character_success(self, db_session, test_user):
        """Test successful character creation"""
        service = CharacterService(db_session)
        
        character_data = {
            "name": "TestWarrior",
            "class": "warrior",
            "race": "human"
        }
        
        character = service.create_character(test_user.id, character_data)
        
        assert character.name == "TestWarrior"
        assert character.character_class == "warrior"
        assert character.level == 1
        assert character.user_id == test_user.id
    
    def test_create_character_duplicate_name(self, db_session, test_user):
        """Test character creation with duplicate name fails"""
        service = CharacterService(db_session)
        
        # Create first character
        character_data = {"name": "DuplicateName", "class": "warrior"}
        service.create_character(test_user.id, character_data)
        
        # Attempt to create duplicate
        with pytest.raises(CharacterError, match="Character name already exists"):
            service.create_character(test_user.id, character_data)
    
    def test_calculate_starting_stats(self, db_session):
        """Test starting stats calculation for different classes"""
        service = CharacterService(db_session)
        
        warrior_stats = service.calculate_starting_stats("warrior")
        assert warrior_stats["strength"] == 16
        assert warrior_stats["intelligence"] == 8
        
        mage_stats = service.calculate_starting_stats("mage")
        assert mage_stats["strength"] == 8
        assert mage_stats["intelligence"] == 16
    
    @pytest.mark.parametrize("invalid_data,expected_error", [
        ({"name": "", "class": "warrior"}, "Name cannot be empty"),
        ({"name": "ab", "class": "warrior"}, "Name must be at least 3 characters"),
        ({"name": "ValidName", "class": "invalid"}, "Invalid character class"),
        ({"name": "a" * 51, "class": "warrior"}, "Name is too long"),
    ])
    def test_validate_character_data_failures(self, db_session, invalid_data, expected_error):
        """Test character data validation with various invalid inputs"""
        service = CharacterService(db_session)
        
        with pytest.raises(CharacterError, match=expected_error):
            service.validate_character_data(invalid_data)

# backend/tests/unit/test_chat_service.py
import pytest
from unittest.mock import Mock, patch
from backend.services.chat_service import ChatService, ChatError

class TestChatService:
    
    def test_send_message_success(self, db_session, test_user, test_channel):
        """Test successful message sending"""
        service = ChatService(db_session)
        
        message = service.send_message(
            user_id=test_user.id,
            channel_id=test_channel.id,
            content="Hello, world!"
        )
        
        assert message["content"] == "Hello, world!"
        assert message["user_id"] == test_user.id
        assert message["channel_id"] == test_channel.id
    
    def test_rate_limiting(self, db_session, test_user, test_channel):
        """Test message rate limiting"""
        service = ChatService(db_session)
        
        # Send messages up to the limit
        for i in range(30):
            service.send_message(test_user.id, test_channel.id, f"Message {i}")
        
        # Next message should fail
        with pytest.raises(ChatError, match="Rate limit exceeded"):
            service.send_message(test_user.id, test_channel.id, "Rate limited message")
    
    @patch('backend.services.chat_service.ProfanityFilter')
    def test_profanity_filter(self, mock_filter, db_session, test_user, test_channel):
        """Test profanity filtering"""
        mock_filter.return_value.contains_profanity.return_value = True
        
        service = ChatService(db_session)
        
        with pytest.raises(ChatError, match="inappropriate content"):
            service.send_message(test_user.id, test_channel.id, "badword content")
    
    def test_message_pagination(self, db_session, test_user, test_channel):
        """Test message pagination"""
        service = ChatService(db_session)
        
        # Create test messages
        for i in range(100):
            service.send_message(test_user.id, test_channel.id, f"Message {i}")
        
        # Get first page
        messages = service.get_channel_messages(test_channel.id, limit=20)
        assert len(messages) == 20
        
        # Get second page using timestamp
        before_timestamp = messages[0]["timestamp"]
        older_messages = service.get_channel_messages(
            test_channel.id, 
            limit=20, 
            before_timestamp=before_timestamp
        )
        assert len(older_messages) == 20
        assert older_messages[0]["content"] != messages[0]["content"]
```

### 2. Integration Testing

#### API Endpoint Testing
```python
# backend/tests/integration/test_api_endpoints.py
import pytest
from fastapi import status

class TestCharacterAPI:
    
    def test_create_character_endpoint(self, client, auth_headers):
        """Test character creation API endpoint"""
        character_data = {
            "name": "APITestCharacter",
            "class": "warrior",
            "race": "elf"
        }
        
        response = client.post(
            "/api/characters",
            json=character_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "APITestCharacter"
    
    def test_get_characters_endpoint(self, client, auth_headers):
        """Test get characters API endpoint"""
        # Create test character first
        client.post("/api/characters", json={
            "name": "TestChar1",
            "class": "warrior"
        }, headers=auth_headers)
        
        response = client.get("/api/characters", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        assert data[0]["name"] == "TestChar1"
    
    def test_unauthorized_access(self, client):
        """Test that unauthorized requests are rejected"""
        response = client.get("/api/characters")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

class TestChatAPI:
    
    def test_send_message_endpoint(self, client, auth_headers, test_channel):
        """Test chat message sending endpoint"""
        message_data = {
            "content": "Test message from API"
        }
        
        response = client.post(
            f"/api/chat/channels/{test_channel.id}/messages",
            json=message_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["content"] == "Test message from API"
    
    def test_get_messages_endpoint(self, client, auth_headers, test_channel):
        """Test get messages endpoint"""
        # Send a test message first
        client.post(
            f"/api/chat/channels/{test_channel.id}/messages",
            json={"content": "Test message"},
            headers=auth_headers
        )
        
        response = client.get(
            f"/api/chat/channels/{test_channel.id}/messages",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        messages = response.json()
        assert len(messages) >= 1
        assert messages[0]["content"] == "Test message"
```

#### WebSocket Testing
```python
# backend/tests/integration/test_websocket_connections.py
import pytest
import json
from fastapi.testclient import TestClient

class TestWebSocketConnections:
    
    def test_websocket_connection(self, client, test_user, test_channel):
        """Test WebSocket connection establishment"""
        with client.websocket_connect(f"/api/chat/ws/{test_channel.id}?token=test_token") as websocket:
            # Test connection is established
            assert websocket is not None
            
            # Send ping
            websocket.send_json({"type": "ping"})
            
            # Receive pong
            response = websocket.receive_json()
            assert response["type"] == "pong"
    
    def test_websocket_message_broadcasting(self, client, test_channel):
        """Test message broadcasting via WebSocket"""
        # Connect two clients
        with client.websocket_connect(f"/api/chat/ws/{test_channel.id}?token=token1") as ws1:
            with client.websocket_connect(f"/api/chat/ws/{test_channel.id}?token=token2") as ws2:
                
                # Send message via API (which should broadcast to WebSocket)
                client.post(
                    f"/api/chat/channels/{test_channel.id}/messages",
                    json={"content": "Broadcast test"}
                )
                
                # Both clients should receive the message
                message1 = ws1.receive_json()
                message2 = ws2.receive_json()
                
                assert message1["type"] == "new_message"
                assert message2["type"] == "new_message"
                assert message1["data"]["content"] == "Broadcast test"
```

### 3. Performance Testing

#### Load Testing with pytest-benchmark
```python
# backend/tests/performance/test_api_performance.py
import pytest

class TestAPIPerformance:
    
    def test_character_creation_performance(self, benchmark, client, auth_headers):
        """Benchmark character creation performance"""
        def create_character():
            response = client.post("/api/characters", json={
                "name": f"PerfTestChar",
                "class": "warrior"
            }, headers=auth_headers)
            return response
        
        result = benchmark(create_character)
        assert result.status_code == 200
    
    def test_message_retrieval_performance(self, benchmark, client, auth_headers, test_channel_with_messages):
        """Benchmark message retrieval performance"""
        def get_messages():
            response = client.get(
                f"/api/chat/channels/{test_channel_with_messages.id}/messages?limit=50",
                headers=auth_headers
            )
            return response
        
        result = benchmark(get_messages)
        assert result.status_code == 200
        assert len(result.json()) <= 50
```

## Frontend Testing Strategy

### 1. Unit Testing with Jest

#### Test Structure
```
frontend/tests/
├── setup.js                 # Test configuration
├── __mocks__/               # Mock implementations
│   ├── websocket.js
│   └── fetch.js
├── unit/
│   ├── api-client.test.js
│   ├── chat-component.test.js
│   └── auth-service.test.js
├── integration/
│   ├── chat-flow.test.js
│   └── character-creation.test.js
└── e2e/
    └── cypress/
        ├── integration/
        └── fixtures/
```

#### Jest Configuration
```javascript
// frontend/jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/js/$1'
  },
  collectCoverageFrom: [
    'js/**/*.js',
    '!js/**/*.test.js',
    '!js/vendor/**'
  ],
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70
    }
  }
};
```

#### Unit Test Examples
```javascript
// frontend/tests/unit/api-client.test.js
import { GameAPIClient } from '../../js/api-client.js';

// Mock fetch
global.fetch = jest.fn();

describe('GameAPIClient', () => {
  let client;
  
  beforeEach(() => {
    client = new GameAPIClient('http://localhost:8000/api', 'test-token');
    fetch.mockClear();
  });
  
  describe('getChannels', () => {
    it('should fetch channels successfully', async () => {
      const mockChannels = [
        { id: 1, name: 'general', display_name: 'General Chat' }
      ];
      
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockChannels
      });
      
      const result = await client.getChannels();
      
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/chat/channels',
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer test-token'
          })
        })
      );
      expect(result).toEqual(mockChannels);
    });
    
    it('should throw error on failed request', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 401
      });
      
      await expect(client.getChannels()).rejects.toThrow('Failed to fetch channels');
    });
  });
  
  describe('sendMessage', () => {
    it('should send message with correct payload', async () => {
      const mockResponse = {
        message_id: 123,
        content: 'Test message',
        timestamp: '2025-01-01T10:00:00Z'
      };
      
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });
      
      const result = await client.sendMessage(1, 'Test message', 42);
      
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/chat/channels/1/messages',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test-token'
          }),
          body: JSON.stringify({
            content: 'Test message',
            character_id: 42
          })
        })
      );
      expect(result).toEqual(mockResponse);
    });
  });
});

// frontend/tests/unit/chat-component.test.js
import { ChatComponent } from '../../js/chat-component.js';

// Mock DOM
document.body.innerHTML = '<div id="test-container"></div>';

// Mock dependencies
const mockAPIClient = {
  getChannels: jest.fn(),
  getChannelMessages: jest.fn(),
  sendMessage: jest.fn()
};

const mockWSClient = {
  connect: jest.fn(),
  disconnect: jest.fn(),
  on: jest.fn(),
  sendTypingNotification: jest.fn()
};

describe('ChatComponent', () => {
  let chatComponent;
  
  beforeEach(() => {
    mockAPIClient.getChannels.mockResolvedValue([
      { id: 1, display_name: 'General' }
    ]);
    mockAPIClient.getChannelMessages.mockResolvedValue([]);
    
    chatComponent = new ChatComponent('test-container', mockAPIClient, mockWSClient);
  });
  
  it('should render chat interface', () => {
    const container = document.getElementById('test-container');
    expect(container.querySelector('.chat-container')).toBeTruthy();
    expect(container.querySelector('#channel-select')).toBeTruthy();
    expect(container.querySelector('#message-input')).toBeTruthy();
  });
  
  it('should load channels on initialization', () => {
    expect(mockAPIClient.getChannels).toHaveBeenCalled();
  });
  
  it('should switch channels correctly', async () => {
    mockAPIClient.getChannelMessages.mockResolvedValue([
      { message_id: 1, content: 'Test message', username: 'testuser' }
    ]);
    
    await chatComponent.switchChannel(1);
    
    expect(mockAPIClient.getChannelMessages).toHaveBeenCalledWith(1, 50, null);
    expect(mockWSClient.connect).toHaveBeenCalledWith(1);
  });
  
  it('should handle message sending', async () => {
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    
    chatComponent.currentChannel = 1;
    messageInput.value = 'Test message';
    
    mockAPIClient.sendMessage.mockResolvedValue({
      message_id: 123,
      content: 'Test message'
    });
    
    await chatComponent.sendMessage();
    
    expect(mockAPIClient.sendMessage).toHaveBeenCalledWith(1, 'Test message', null);
    expect(messageInput.value).toBe('');
  });
  
  it('should handle WebSocket events', () => {
    const newMessage = {
      message_id: 123,
      content: 'New message',
      username: 'otheruser',
      timestamp: '2025-01-01T10:00:00Z'
    };
    
    // Simulate WebSocket event handler registration
    const eventHandlers = {};
    mockWSClient.on.mockImplementation((event, handler) => {
      eventHandlers[event] = handler;
    });
    
    // Re-initialize to register handlers
    chatComponent = new ChatComponent('test-container', mockAPIClient, mockWSClient);
    
    // Simulate new message event
    eventHandlers.newMessage(newMessage);
    
    // Check if message was added to the DOM
    const messageElements = document.querySelectorAll('.message');
    expect(messageElements.length).toBeGreaterThan(0);
  });
});
```

### 2. Integration Testing

#### API Integration Tests
```javascript
// frontend/tests/integration/chat-flow.test.js
import { GameAPIClient } from '../../js/api-client.js';
import { ChatWebSocketClient } from '../../js/chat-websocket.js';

// Use actual server for integration tests
const API_BASE_URL = 'http://localhost:8000/api';
const WS_BASE_URL = 'ws://localhost:8000/api';

describe('Chat Integration Flow', () => {
  let apiClient;
  let wsClient;
  let authToken;
  
  beforeAll(async () => {
    // Create test user and get auth token
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: 'integrationtestuser',
        email: 'integration@test.com',
        password: 'testpassword'
      })
    });
    
    const loginResponse = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      body: new URLSearchParams({
        username: 'integrationtestuser',
        password: 'testpassword'
      })
    });
    
    const loginData = await loginResponse.json();
    authToken = loginData.access_token;
    
    apiClient = new GameAPIClient(API_BASE_URL, authToken);
    wsClient = new ChatWebSocketClient(WS_BASE_URL, authToken);
  });
  
  it('should complete full chat workflow', async () => {
    // 1. Get available channels
    const channels = await apiClient.getChannels();
    expect(channels.length).toBeGreaterThan(0);
    
    const testChannel = channels[0];
    
    // 2. Connect to WebSocket
    const messagePromise = new Promise((resolve) => {
      wsClient.on('newMessage', resolve);
    });
    
    wsClient.connect(testChannel.id);
    
    // Wait for connection
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // 3. Send message via API
    const messageContent = 'Integration test message';
    const sentMessage = await apiClient.sendMessage(testChannel.id, messageContent);
    
    expect(sentMessage.content).toBe(messageContent);
    
    // 4. Verify WebSocket receives the message
    const receivedMessage = await messagePromise;
    expect(receivedMessage.content).toBe(messageContent);
    
    // 5. Get messages via API to verify persistence
    const messages = await apiClient.getChannelMessages(testChannel.id);
    const foundMessage = messages.find(m => m.content === messageContent);
    expect(foundMessage).toBeTruthy();
    
    // Cleanup
    wsClient.disconnect();
  });
});
```

### 3. End-to-End Testing with Cypress

#### Cypress Configuration
```javascript
// frontend/cypress.config.js
const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:8080',
    supportFile: 'cypress/support/e2e.js',
    specPattern: 'cypress/e2e/**/*.cy.js',
    viewportWidth: 1280,
    viewportHeight: 720,
    env: {
      apiUrl: 'http://localhost:8000/api'
    }
  }
});
```

#### E2E Test Examples
```javascript
// frontend/cypress/e2e/chat-functionality.cy.js
describe('Chat Functionality', () => {
  beforeEach(() => {
    // Login before each test
    cy.login('testuser', 'testpassword');
    cy.visit('/');
  });
  
  it('should allow user to join a channel and send messages', () => {
    // Navigate to chat
    cy.get('[data-testid="chat-tab"]').click();
    
    // Select a channel
    cy.get('#channel-select').select('General');
    
    // Wait for messages to load
    cy.get('.messages-list').should('be.visible');
    
    // Type and send a message
    const testMessage = 'Test message from Cypress';
    cy.get('#message-input').type(testMessage);
    cy.get('#send-button').click();
    
    // Verify message appears in chat
    cy.get('.message').should('contain', testMessage);
    
    // Verify input is cleared
    cy.get('#message-input').should('have.value', '');
  });
  
  it('should show typing indicators', () => {
    cy.get('#channel-select').select('General');
    
    // Start typing
    cy.get('#message-input').type('Test typing');
    
    // Should trigger typing indicator (this would need WebSocket mocking)
    cy.get('#typing-indicator').should('not.have.class', 'hidden');
    
    // Stop typing - indicator should disappear after timeout
    cy.wait(3000);
    cy.get('#typing-indicator').should('have.class', 'hidden');
  });
  
  it('should handle connection status updates', () => {
    cy.get('#channel-select').select('General');
    
    // Check initial connection status
    cy.get('#connection-status').should('contain', 'connected');
    
    // Simulate connection loss (would need server control)
    // cy.mockWebSocketDisconnect();
    // cy.get('#connection-status').should('contain', 'disconnected');
  });
});

// frontend/cypress/e2e/character-management.cy.js
describe('Character Management', () => {
  beforeEach(() => {
    cy.login('testuser', 'testpassword');
    cy.visit('/');
  });
  
  it('should create a new character', () => {
    cy.get('[data-testid="characters-tab"]').click();
    cy.get('[data-testid="create-character-btn"]').click();
    
    // Fill character creation form
    cy.get('#character-name').type('CypressTestChar');
    cy.get('#character-class').select('warrior');
    cy.get('#character-race').select('human');
    
    // Submit form
    cy.get('[data-testid="create-character-submit"]').click();
    
    // Verify character appears in list
    cy.get('[data-testid="character-list"]').should('contain', 'CypressTestChar');
    
    // Verify character details are correct
    cy.get('[data-testid="character-card"]').first().within(() => {
      cy.get('.character-name').should('contain', 'CypressTestChar');
      cy.get('.character-class').should('contain', 'warrior');
      cy.get('.character-level').should('contain', '1');
    });
  });
  
  it('should validate character creation form', () => {
    cy.get('[data-testid="characters-tab"]').click();
    cy.get('[data-testid="create-character-btn"]').click();
    
    // Try to submit empty form
    cy.get('[data-testid="create-character-submit"]').click();
    
    // Should show validation errors
    cy.get('.error-message').should('contain', 'Name is required');
    
    // Fill name that's too short
    cy.get('#character-name').type('ab');
    cy.get('[data-testid="create-character-submit"]').click();
    
    cy.get('.error-message').should('contain', 'Name must be at least 3 characters');
  });
});
```

#### Custom Cypress Commands
```javascript
// frontend/cypress/support/commands.js
Cypress.Commands.add('login', (username, password) => {
  cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/auth/login`,
    body: new URLSearchParams({
      username: username,
      password: password
    }),
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  }).then((response) => {
    const token = response.body.access_token;
    window.localStorage.setItem('authToken', token);
  });
});

Cypress.Commands.add('createTestCharacter', (characterData) => {
  const token = window.localStorage.getItem('authToken');
  
  cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/characters`,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: characterData
  });
});
```

## API Contract Testing

### Contract Testing with Pact

#### Consumer Tests (Frontend)
```javascript
// frontend/tests/contract/chat-api.pact.test.js
import { Pact } from '@pact-foundation/pact';
import { GameAPIClient } from '../../js/api-client.js';

describe('Chat API Contract', () => {
  const provider = new Pact({
    consumer: 'GameFrontend',
    provider: 'GameBackend',
    port: 1234,
    log: path.resolve(process.cwd(), 'logs', 'pact.log'),
    dir: path.resolve(process.cwd(), 'pacts'),
    logLevel: 'INFO'
  });
  
  beforeAll(() => provider.setup());
  afterAll(() => provider.finalize());
  afterEach(() => provider.verify());
  
  it('should get channels successfully', async () => {
    await provider.addInteraction({
      state: 'user is authenticated',
      uponReceiving: 'a request for channels',
      withRequest: {
        method: 'GET',
        path: '/api/chat/channels',
        headers: {
          'Authorization': 'Bearer valid-token'
        }
      },
      willRespondWith: {
        status: 200,
        headers: {
          'Content-Type': 'application/json'
        },
        body: [
          {
            id: 1,
            name: 'general',
            display_name: 'General Chat',
            type: 'public'
          }
        ]
      }
    });
    
    const client = new GameAPIClient('http://localhost:1234/api', 'valid-token');
    const channels = await client.getChannels();
    
    expect(channels).toHaveLength(1);
    expect(channels[0].name).toBe('general');
  });
});
```

#### Provider Tests (Backend)
```python
# backend/tests/contract/test_pact_provider.py
import pytest
from pact import Verifier

def test_pact_verification():
    """Verify that the backend satisfies frontend contracts"""
    verifier = Verifier(
        provider='GameBackend',
        provider_base_url='http://localhost:8000'
    )
    
    # Set up provider states
    verifier.setup_states({
        'user is authenticated': setup_authenticated_user,
        'channel exists': setup_test_channel
    })
    
    # Verify against pact files
    verifier.verify_pacts('../frontend/pacts/gamefrontend-gamebackend.json')

def setup_authenticated_user():
    """Set up authenticated user state"""
    # Create test user and return auth token
    pass

def setup_test_channel():
    """Set up test channel state"""
    # Create test channel
    pass
```

## Continuous Integration Pipeline

### GitHub Actions Workflow
```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-benchmark
    
    - name: Run unit tests
      run: |
        cd backend
        pytest tests/unit/ -v --cov=. --cov-report=xml
    
    - name: Run integration tests
      run: |
        cd backend
        pytest tests/integration/ -v
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml

  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '16'
    
    - name: Install dependencies
      run: |
        cd frontend
        npm install
    
    - name: Run unit tests
      run: |
        cd frontend
        npm run test:unit -- --coverage
    
    - name: Run linting
      run: |
        cd frontend
        npm run lint
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./frontend/coverage/lcov.info

  e2e-tests:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up services
      run: |
        docker-compose -f docker-compose.test.yml up -d
        sleep 30  # Wait for services to be ready
    
    - name: Run E2E tests
      run: |
        cd frontend
        npm run test:e2e:headless
    
    - name: Upload test artifacts
      uses: actions/upload-artifact@v3
      if: failure()
      with:
        name: cypress-screenshots
        path: frontend/cypress/screenshots

  contract-tests:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Run contract tests
      run: |
        # Run frontend contract tests (consumer)
        cd frontend
        npm run test:contract
        
        # Start backend for provider verification
        cd ../backend
        python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
        sleep 10
        
        # Run provider verification
        pytest tests/contract/
```

## Performance and Load Testing

### Backend Load Testing with Locust
```python
# backend/tests/load/locustfile.py
from locust import HttpUser, task, between
import json

class GameAPIUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login and get auth token"""
        response = self.client.post("/api/auth/login", data={
            "username": "loadtestuser",
            "password": "loadtestpass"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def get_characters(self):
        """Get user characters"""
        self.client.get("/api/characters", headers=self.headers)
    
    @task(2)
    def get_chat_messages(self):
        """Get chat messages"""
        self.client.get("/api/chat/channels/1/messages", headers=self.headers)
    
    @task(1)
    def send_chat_message(self):
        """Send a chat message"""
        self.client.post(
            "/api/chat/channels/1/messages",
            json={"content": "Load test message"},
            headers=self.headers
        )
    
    @task(1)
    def create_character(self):
        """Create a new character"""
        self.client.post(
            "/api/characters",
            json={
                "name": f"LoadTestChar{self.user_id}",
                "class": "warrior"
            },
            headers=self.headers
        )
```

### Frontend Performance Testing
```javascript
// frontend/tests/performance/performance.test.js
import { performance } from 'perf_hooks';

describe('Frontend Performance', () => {
  it('should render chat component within performance budget', async () => {
    const start = performance.now();
    
    // Initialize chat component
    const chatComponent = new ChatComponent('test-container', mockAPIClient, mockWSClient);
    
    const end = performance.now();
    const renderTime = end - start;
    
    // Component should render within 100ms
    expect(renderTime).toBeLessThan(100);
  });
  
  it('should handle large message lists efficiently', async () => {
    const messages = Array.from({ length: 1000 }, (_, i) => ({
      message_id: i,
      content: `Message ${i}`,
      username: 'testuser',
      timestamp: new Date().toISOString()
    }));
    
    const start = performance.now();
    
    // Render large message list
    chatComponent.messages = messages;
    chatComponent.renderMessages();
    
    const end = performance.now();
    const renderTime = end - start;
    
    // Should render 1000 messages within 500ms
    expect(renderTime).toBeLessThan(500);
  });
});
```

## Monitoring and Alerting

### Test Metrics Dashboard
```yaml
# monitoring/test-metrics.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - ./grafana/dashboards:/var/lib/grafana/dashboards
```

### Test Quality Gates
```python
# scripts/quality_gate.py
import json
import sys

def check_coverage_threshold(coverage_file, threshold=80):
    """Check if test coverage meets threshold"""
    with open(coverage_file) as f:
        coverage_data = json.load(f)
    
    total_coverage = coverage_data['totals']['percent_covered']
    
    if total_coverage < threshold:
        print(f"Coverage {total_coverage}% below threshold {threshold}%")
        return False
    
    return True

def check_test_results(results_file):
    """Check test results for failures"""
    with open(results_file) as f:
        results = json.load(f)
    
    if results['failed'] > 0:
        print(f"Tests failed: {results['failed']}")
        return False
    
    return True

if __name__ == "__main__":
    coverage_ok = check_coverage_threshold('coverage.json')
    tests_ok = check_test_results('test_results.json')
    
    if not (coverage_ok and tests_ok):
        sys.exit(1)
    
    print("All quality gates passed!")
```

## Summary

This comprehensive testing strategy ensures:

- **Reliability**: Multiple layers of testing catch different types of issues
- **Confidence**: Automated tests provide confidence in deployments
- **Performance**: Load testing ensures the system can handle expected traffic
- **Contract Compliance**: API contracts prevent integration issues
- **Quality**: Coverage metrics and quality gates maintain code quality

### Key Testing Tools

**Backend**:
- pytest for unit/integration testing
- TestClient for API testing
- Locust for load testing
- Pact for contract testing

**Frontend**:
- Jest for unit testing
- Cypress for E2E testing
- Performance API for performance testing

**Integration**:
- Docker Compose for test environments
- GitHub Actions for CI/CD
- Prometheus/Grafana for monitoring

This strategy provides a solid foundation for maintaining a reliable, performant game architecture with confidence in both backend and frontend components.