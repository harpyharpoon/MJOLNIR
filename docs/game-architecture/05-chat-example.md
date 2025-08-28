# Example Implementation: Chat Broadcasting

## Overview

This document provides a complete, working example of converting a chat message broadcasting function from a monolithic backend into a Python backend API endpoint with corresponding JavaScript frontend code. This serves as a practical demonstration of the separation principles outlined in the architecture guides.

## Original Monolithic Implementation

### Legacy Chat System (Hypothetical)
```python
# legacy_chat.py - Original monolithic implementation
import sqlite3
import json
from datetime import datetime
from flask import Flask, render_template, request, session

app = Flask(__name__)

class LegacyChatSystem:
    def __init__(self):
        self.db_path = "chat.db"
        self.setup_database()
    
    def setup_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                username TEXT,
                message TEXT,
                channel TEXT,
                timestamp TEXT
            )
        ''')
        conn.close()
    
    def display_chat_page(self, channel="general"):
        """Generate HTML page with chat interface and messages"""
        # Mixed UI and logic - PROBLEM!
        messages = self.get_recent_messages(channel)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Game Chat</title>
            <script>
                function sendMessage() {{
                    var message = document.getElementById('messageInput').value;
                    var xhr = new XMLHttpRequest();
                    xhr.open('POST', '/send_message', true);
                    xhr.setRequestHeader('Content-Type', 'application/json');
                    xhr.send(JSON.stringify({{
                        'message': message,
                        'channel': '{channel}'
                    }}));
                    document.getElementById('messageInput').value = '';
                    setTimeout(function() {{ location.reload(); }}, 500);
                }}
            </script>
        </head>
        <body>
            <div id="chat-container">
                <div id="messages">
        """
        
        for msg in messages:
            html += f"""
                <div class="message">
                    <span class="username">{msg['username']}</span>:
                    <span class="content">{msg['message']}</span>
                    <span class="timestamp">{msg['timestamp']}</span>
                </div>
            """
        
        html += """
                </div>
                <div id="input-area">
                    <input type="text" id="messageInput" placeholder="Type a message...">
                    <button onclick="sendMessage()">Send</button>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def get_recent_messages(self, channel, limit=50):
        """Get recent messages for a channel"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT username, message, timestamp FROM messages WHERE channel = ? ORDER BY id DESC LIMIT ?",
            (channel, limit)
        )
        messages = [
            {"username": row[0], "message": row[1], "timestamp": row[2]}
            for row in cursor.fetchall()
        ]
        conn.close()
        return list(reversed(messages))
    
    def send_message(self, username, message, channel="general"):
        """Send a message and broadcast to all users"""
        # Validation mixed with storage - PROBLEM!
        if not message or len(message.strip()) == 0:
            return {"error": "Message cannot be empty"}
        
        if len(message) > 500:
            return {"error": "Message too long"}
        
        # Profanity filter - business logic
        if self.contains_profanity(message):
            return {"error": "Message contains inappropriate content"}
        
        # Store message
        timestamp = datetime.now().isoformat()
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO messages (username, message, channel, timestamp) VALUES (?, ?, ?, ?)",
            (username, message, channel, timestamp)
        )
        conn.commit()
        conn.close()
        
        # Broadcast to all connected clients (simplified)
        self.broadcast_to_clients({
            "type": "new_message",
            "username": username,
            "message": message,
            "channel": channel,
            "timestamp": timestamp
        })
        
        return {"success": True, "message_id": conn.lastrowid}
    
    def contains_profanity(self, message):
        """Simple profanity filter"""
        banned_words = ["spam", "badword1", "badword2"]
        return any(word in message.lower() for word in banned_words)
    
    def broadcast_to_clients(self, data):
        """Broadcast message to all connected clients"""
        # Simplified - in reality would use WebSockets
        print(f"Broadcasting: {data}")

# Flask routes
chat_system = LegacyChatSystem()

@app.route('/chat/<channel>')
def chat_page(channel):
    return chat_system.display_chat_page(channel)

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    username = session.get('username', 'Anonymous')
    result = chat_system.send_message(
        username, 
        data['message'], 
        data.get('channel', 'general')
    )
    return json.dumps(result)
```

## Converted Architecture

### Backend Implementation (Python/FastAPI)

#### 1. Data Models
```python
# backend/models/chat.py
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class ChatChannel(Base):
    __tablename__ = "chat_channels"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    display_name = Column(String(100))
    description = Column(Text)
    channel_type = Column(String(20), default="public")  # public, private, guild
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    messages = relationship("ChatMessage", back_populates="channel")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    channel_id = Column(Integer, ForeignKey("chat_channels.id"))
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=True)
    content = Column(Text)
    message_type = Column(String(20), default="text")  # text, system, emote
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    edited_at = Column(DateTime(timezone=True), nullable=True)
    
    user = relationship("User")
    channel = relationship("ChatChannel", back_populates="messages")
    character = relationship("Character")
```

#### 2. Service Layer
```python
# backend/services/chat_service.py
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
from ..models.chat import ChatMessage, ChatChannel
from ..models.user import User
from ..models.character import Character
from .profanity_filter import ProfanityFilter

class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.profanity_filter = ProfanityFilter()
        self.rate_limit_cache = {}  # In production, use Redis
    
    def get_channel_messages(
        self, 
        channel_id: int, 
        limit: int = 50, 
        before_timestamp: Optional[datetime] = None
    ) -> List[dict]:
        """Get messages for a channel with pagination"""
        query = self.db.query(ChatMessage).filter(
            ChatMessage.channel_id == channel_id
        ).order_by(ChatMessage.created_at.desc())
        
        if before_timestamp:
            query = query.filter(ChatMessage.created_at < before_timestamp)
        
        messages = query.limit(limit).all()
        
        return [self._format_message(msg) for msg in reversed(messages)]
    
    def send_message(
        self, 
        user_id: int, 
        channel_id: int, 
        content: str, 
        character_id: Optional[int] = None
    ) -> dict:
        """Send a chat message with validation and rate limiting"""
        
        # Rate limiting
        if not self._check_rate_limit(user_id):
            raise ChatError("Rate limit exceeded. Please slow down.")
        
        # Content validation
        self._validate_message_content(content)
        
        # Channel permission check
        if not self._can_user_post_to_channel(user_id, channel_id):
            raise ChatError("You don't have permission to post in this channel.")
        
        # Profanity filter
        if self.profanity_filter.contains_profanity(content):
            raise ChatError("Message contains inappropriate content.")
        
        # Create message
        message = ChatMessage(
            user_id=user_id,
            channel_id=channel_id,
            character_id=character_id,
            content=content,
            message_type="text"
        )
        
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        
        # Update rate limit
        self._update_rate_limit(user_id)
        
        return self._format_message(message)
    
    def _validate_message_content(self, content: str):
        """Validate message content"""
        if not content or not content.strip():
            raise ChatError("Message cannot be empty")
        
        if len(content) > 1000:
            raise ChatError("Message is too long (max 1000 characters)")
        
        if len(content.strip()) < 1:
            raise ChatError("Message cannot be only whitespace")
    
    def _check_rate_limit(self, user_id: int) -> bool:
        """Check if user is within rate limits"""
        now = datetime.now()
        user_timestamps = self.rate_limit_cache.get(user_id, [])
        
        # Remove timestamps older than 1 minute
        user_timestamps = [
            ts for ts in user_timestamps 
            if now - ts < timedelta(minutes=1)
        ]
        
        # Check if under limit (30 messages per minute)
        return len(user_timestamps) < 30
    
    def _update_rate_limit(self, user_id: int):
        """Update rate limit tracking"""
        now = datetime.now()
        if user_id not in self.rate_limit_cache:
            self.rate_limit_cache[user_id] = []
        
        self.rate_limit_cache[user_id].append(now)
    
    def _can_user_post_to_channel(self, user_id: int, channel_id: int) -> bool:
        """Check if user can post to channel"""
        channel = self.db.query(ChatChannel).filter(
            ChatChannel.id == channel_id
        ).first()
        
        if not channel:
            return False
        
        if channel.channel_type == "public":
            return True
        
        # Add more complex permission logic here
        return True
    
    def _format_message(self, message: ChatMessage) -> dict:
        """Format message for API response"""
        return {
            "message_id": message.id,
            "user_id": message.user_id,
            "username": message.user.username,
            "character_name": message.character.name if message.character else None,
            "character_id": message.character_id,
            "content": message.content,
            "message_type": message.message_type,
            "timestamp": message.created_at.isoformat(),
            "channel_id": message.channel_id
        }

class ChatError(Exception):
    pass
```

#### 3. API Endpoints
```python
# backend/api/chat.py
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..models.database import get_db
from ..services.chat_service import ChatService, ChatError
from ..services.auth_service import get_current_user
from ..schemas.chat import MessageCreate, MessageResponse, ChannelResponse
from ..websocket.chat_manager import chat_manager

router = APIRouter()

@router.get("/channels", response_model=List[ChannelResponse])
async def get_channels(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available chat channels for user"""
    chat_service = ChatService(db)
    channels = chat_service.get_user_channels(current_user.id)
    return channels

@router.get("/channels/{channel_id}/messages", response_model=List[MessageResponse])
async def get_channel_messages(
    channel_id: int,
    limit: int = 50,
    before: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get messages for a specific channel"""
    chat_service = ChatService(db)
    
    before_timestamp = None
    if before:
        try:
            before_timestamp = datetime.fromisoformat(before)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid timestamp format")
    
    try:
        messages = chat_service.get_channel_messages(
            channel_id, limit, before_timestamp
        )
        return messages
    except ChatError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/channels/{channel_id}/messages", response_model=MessageResponse)
async def send_message(
    channel_id: int,
    message_data: MessageCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message to a channel"""
    chat_service = ChatService(db)
    
    try:
        message = chat_service.send_message(
            user_id=current_user.id,
            channel_id=channel_id,
            content=message_data.content,
            character_id=message_data.character_id
        )
        
        # Broadcast to WebSocket clients
        await chat_manager.broadcast_to_channel(channel_id, {
            "type": "new_message",
            "data": message
        })
        
        return message
        
    except ChatError as e:
        raise HTTPException(status_code=400, detail=str(e))

# WebSocket endpoint for real-time chat
@router.websocket("/ws/{channel_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    channel_id: int,
    token: str,  # Pass token as query parameter
    db: Session = Depends(get_db)
):
    # Authenticate user from token
    user = await authenticate_websocket_user(token, db)
    if not user:
        await websocket.close(code=4001, reason="Unauthorized")
        return
    
    await chat_manager.connect(websocket, user.id, channel_id)
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_json()
            
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            elif data.get("type") == "typing":
                # Broadcast typing indicator
                await chat_manager.broadcast_to_channel(
                    channel_id, 
                    {
                        "type": "user_typing",
                        "user_id": user.id,
                        "username": user.username
                    },
                    exclude_user=user.id
                )
    
    except WebSocketDisconnect:
        chat_manager.disconnect(websocket, user.id, channel_id)
```

#### 4. WebSocket Manager
```python
# backend/websocket/chat_manager.py
from fastapi import WebSocket
from typing import Dict, List, Set
import json

class ChatConnectionManager:
    def __init__(self):
        # Channel ID -> Set of WebSocket connections
        self.channel_connections: Dict[int, Set[WebSocket]] = {}
        # User ID -> WebSocket connection
        self.user_connections: Dict[int, WebSocket] = {}
        # WebSocket -> User ID mapping
        self.connection_users: Dict[WebSocket, int] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int, channel_id: int):
        """Connect user to a channel"""
        await websocket.accept()
        
        # Add to channel connections
        if channel_id not in self.channel_connections:
            self.channel_connections[channel_id] = set()
        self.channel_connections[channel_id].add(websocket)
        
        # Track user connection
        self.user_connections[user_id] = websocket
        self.connection_users[websocket] = user_id
        
        # Notify channel about user joining
        await self.broadcast_to_channel(channel_id, {
            "type": "user_joined",
            "user_id": user_id
        }, exclude_connection=websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: int, channel_id: int):
        """Disconnect user from channel"""
        # Remove from channel connections
        if channel_id in self.channel_connections:
            self.channel_connections[channel_id].discard(websocket)
            if not self.channel_connections[channel_id]:
                del self.channel_connections[channel_id]
        
        # Remove user tracking
        self.user_connections.pop(user_id, None)
        self.connection_users.pop(websocket, None)
        
        # Notify channel about user leaving (async task)
        asyncio.create_task(self.broadcast_to_channel(channel_id, {
            "type": "user_left",
            "user_id": user_id
        }))
    
    async def broadcast_to_channel(
        self, 
        channel_id: int, 
        message: dict, 
        exclude_connection: WebSocket = None,
        exclude_user: int = None
    ):
        """Broadcast message to all connections in a channel"""
        if channel_id not in self.channel_connections:
            return
        
        message_str = json.dumps(message)
        disconnected = []
        
        for connection in self.channel_connections[channel_id]:
            if connection == exclude_connection:
                continue
            
            if exclude_user and self.connection_users.get(connection) == exclude_user:
                continue
            
            try:
                await connection.send_text(message_str)
            except:
                # Connection is dead, mark for removal
                disconnected.append(connection)
        
        # Clean up dead connections
        for conn in disconnected:
            user_id = self.connection_users.get(conn)
            if user_id:
                self.disconnect(conn, user_id, channel_id)
    
    async def send_to_user(self, user_id: int, message: dict):
        """Send message to specific user"""
        if user_id in self.user_connections:
            try:
                await self.user_connections[user_id].send_text(json.dumps(message))
            except:
                # Connection is dead, clean up
                del self.user_connections[user_id]

# Global instance
chat_manager = ChatConnectionManager()
```

### Frontend Implementation (JavaScript)

#### 1. Chat API Client
```javascript
// frontend/js/chat-api-client.js
class ChatAPIClient {
    constructor(baseURL, authToken) {
        this.baseURL = baseURL;
        this.authToken = authToken;
    }
    
    async getChannels() {
        const response = await fetch(`${this.baseURL}/chat/channels`, {
            headers: {
                'Authorization': `Bearer ${this.authToken}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch channels');
        }
        
        return response.json();
    }
    
    async getChannelMessages(channelId, limit = 50, before = null) {
        let url = `${this.baseURL}/chat/channels/${channelId}/messages?limit=${limit}`;
        if (before) {
            url += `&before=${encodeURIComponent(before)}`;
        }
        
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${this.authToken}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch messages');
        }
        
        return response.json();
    }
    
    async sendMessage(channelId, content, characterId = null) {
        const response = await fetch(`${this.baseURL}/chat/channels/${channelId}/messages`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.authToken}`
            },
            body: JSON.stringify({
                content: content,
                character_id: characterId
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to send message');
        }
        
        return response.json();
    }
}
```

#### 2. WebSocket Chat Client
```javascript
// frontend/js/chat-websocket.js
class ChatWebSocketClient {
    constructor(wsURL, authToken) {
        this.wsURL = wsURL;
        this.authToken = authToken;
        this.socket = null;
        this.currentChannel = null;
        this.eventHandlers = {};
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }
    
    connect(channelId) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.disconnect();
        }
        
        this.currentChannel = channelId;
        const url = `${this.wsURL}/chat/ws/${channelId}?token=${this.authToken}`;
        
        this.socket = new WebSocket(url);
        
        this.socket.onopen = (event) => {
            console.log('WebSocket connected to channel', channelId);
            this.reconnectAttempts = 0;
            this.emit('connected', { channelId });
        };
        
        this.socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            } catch (error) {
                console.error('Failed to parse WebSocket message:', error);
            }
        };
        
        this.socket.onclose = (event) => {
            console.log('WebSocket disconnected:', event.code, event.reason);
            this.emit('disconnected', { code: event.code, reason: event.reason });
            
            // Attempt to reconnect if not intentional disconnect
            if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
                setTimeout(() => {
                    this.reconnectAttempts++;
                    console.log(`Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
                    this.connect(channelId);
                }, 1000 * this.reconnectAttempts);
            }
        };
        
        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.emit('error', error);
        };
        
        // Send ping every 30 seconds to keep connection alive
        this.pingInterval = setInterval(() => {
            if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                this.socket.send(JSON.stringify({ type: 'ping' }));
            }
        }, 30000);
    }
    
    disconnect() {
        if (this.pingInterval) {
            clearInterval(this.pingInterval);
        }
        
        if (this.socket) {
            this.socket.close(1000, 'Intentional disconnect');
            this.socket = null;
        }
        
        this.currentChannel = null;
    }
    
    handleMessage(data) {
        switch (data.type) {
            case 'new_message':
                this.emit('newMessage', data.data);
                break;
            case 'user_joined':
                this.emit('userJoined', data);
                break;
            case 'user_left':
                this.emit('userLeft', data);
                break;
            case 'user_typing':
                this.emit('userTyping', data);
                break;
            case 'pong':
                // Handle ping response
                break;
            default:
                console.log('Unknown message type:', data.type);
        }
    }
    
    sendTypingNotification() {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({ type: 'typing' }));
        }
    }
    
    on(event, handler) {
        if (!this.eventHandlers[event]) {
            this.eventHandlers[event] = [];
        }
        this.eventHandlers[event].push(handler);
    }
    
    off(event, handler) {
        if (this.eventHandlers[event]) {
            this.eventHandlers[event] = this.eventHandlers[event].filter(h => h !== handler);
        }
    }
    
    emit(event, data) {
        if (this.eventHandlers[event]) {
            this.eventHandlers[event].forEach(handler => handler(data));
        }
    }
}
```

#### 3. Chat UI Component
```javascript
// frontend/js/chat-component.js
class ChatComponent {
    constructor(containerId, apiClient, wsClient) {
        this.container = document.getElementById(containerId);
        this.apiClient = apiClient;
        this.wsClient = wsClient;
        
        this.currentChannel = null;
        this.messages = [];
        this.isLoading = false;
        this.typingUsers = new Set();
        
        this.setupEventHandlers();
        this.render();
    }
    
    setupEventHandlers() {
        // WebSocket event handlers
        this.wsClient.on('newMessage', (message) => {
            this.addMessage(message);
            this.scrollToBottom();
        });
        
        this.wsClient.on('userTyping', (data) => {
            this.showTypingIndicator(data.username);
        });
        
        this.wsClient.on('connected', () => {
            this.setConnectionStatus('connected');
        });
        
        this.wsClient.on('disconnected', () => {
            this.setConnectionStatus('disconnected');
        });
    }
    
    render() {
        this.container.innerHTML = `
            <div class="chat-container">
                <div class="chat-header">
                    <select id="channel-select">
                        <option value="">Select a channel...</option>
                    </select>
                    <div class="connection-status" id="connection-status">Disconnected</div>
                </div>
                
                <div class="chat-messages" id="chat-messages">
                    <div class="loading-indicator hidden" id="loading-indicator">
                        Loading messages...
                    </div>
                    <div class="messages-list" id="messages-list"></div>
                    <div class="typing-indicator hidden" id="typing-indicator">
                        <span id="typing-text"></span>
                    </div>
                </div>
                
                <div class="chat-input">
                    <div class="input-container">
                        <input type="text" id="message-input" placeholder="Type a message..." maxlength="1000">
                        <button id="send-button" disabled>Send</button>
                    </div>
                    <div class="character-selector">
                        <select id="character-select">
                            <option value="">Speaking as yourself</option>
                        </select>
                    </div>
                </div>
            </div>
        `;
        
        this.attachEventListeners();
        this.loadChannels();
    }
    
    attachEventListeners() {
        const channelSelect = document.getElementById('channel-select');
        const messageInput = document.getElementById('message-input');
        const sendButton = document.getElementById('send-button');
        const messagesContainer = document.getElementById('chat-messages');
        
        // Channel selection
        channelSelect.addEventListener('change', (e) => {
            this.switchChannel(parseInt(e.target.value));
        });
        
        // Message input
        messageInput.addEventListener('input', (e) => {
            sendButton.disabled = !e.target.value.trim();
            this.handleTyping();
        });
        
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Send button
        sendButton.addEventListener('click', () => {
            this.sendMessage();
        });
        
        // Scroll to load older messages
        messagesContainer.addEventListener('scroll', () => {
            if (messagesContainer.scrollTop === 0 && !this.isLoading) {
                this.loadOlderMessages();
            }
        });
    }
    
    async loadChannels() {
        try {
            const channels = await this.apiClient.getChannels();
            const channelSelect = document.getElementById('channel-select');
            
            channels.forEach(channel => {
                const option = document.createElement('option');
                option.value = channel.id;
                option.textContent = channel.display_name;
                channelSelect.appendChild(option);
            });
            
        } catch (error) {
            console.error('Failed to load channels:', error);
            this.showError('Failed to load channels');
        }
    }
    
    async switchChannel(channelId) {
        if (channelId === this.currentChannel) return;
        
        // Disconnect from current channel
        if (this.currentChannel) {
            this.wsClient.disconnect();
        }
        
        this.currentChannel = channelId;
        this.messages = [];
        this.clearMessages();
        
        if (channelId) {
            // Load messages and connect to WebSocket
            await this.loadChannelMessages(channelId);
            this.wsClient.connect(channelId);
        }
    }
    
    async loadChannelMessages(channelId, before = null) {
        this.setLoading(true);
        
        try {
            const messages = await this.apiClient.getChannelMessages(channelId, 50, before);
            
            if (before) {
                // Prepend older messages
                this.messages = [...messages, ...this.messages];
            } else {
                // Replace all messages
                this.messages = messages;
            }
            
            this.renderMessages();
            
            if (!before) {
                this.scrollToBottom();
            }
            
        } catch (error) {
            console.error('Failed to load messages:', error);
            this.showError('Failed to load messages');
        } finally {
            this.setLoading(false);
        }
    }
    
    async loadOlderMessages() {
        if (this.messages.length === 0) return;
        
        const oldestMessage = this.messages[0];
        await this.loadChannelMessages(this.currentChannel, oldestMessage.timestamp);
    }
    
    async sendMessage() {
        const messageInput = document.getElementById('message-input');
        const characterSelect = document.getElementById('character-select');
        const content = messageInput.value.trim();
        
        if (!content || !this.currentChannel) return;
        
        const characterId = characterSelect.value || null;
        
        try {
            // Clear input immediately for better UX
            messageInput.value = '';
            document.getElementById('send-button').disabled = true;
            
            // API call will trigger WebSocket broadcast, so message will appear via WebSocket
            await this.apiClient.sendMessage(this.currentChannel, content, characterId);
            
        } catch (error) {
            console.error('Failed to send message:', error);
            this.showError(error.message);
            
            // Restore input on error
            messageInput.value = content;
            document.getElementById('send-button').disabled = false;
        }
    }
    
    addMessage(message) {
        this.messages.push(message);
        this.renderNewMessage(message);
    }
    
    renderMessages() {
        const messagesList = document.getElementById('messages-list');
        messagesList.innerHTML = '';
        
        this.messages.forEach(message => {
            messagesList.appendChild(this.createMessageElement(message));
        });
    }
    
    renderNewMessage(message) {
        const messagesList = document.getElementById('messages-list');
        messagesList.appendChild(this.createMessageElement(message));
    }
    
    createMessageElement(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message';
        messageDiv.dataset.messageId = message.message_id;
        
        const timestamp = new Date(message.timestamp).toLocaleTimeString();
        const displayName = message.character_name || message.username;
        
        messageDiv.innerHTML = `
            <div class="message-header">
                <span class="username">${this.escapeHtml(displayName)}</span>
                <span class="timestamp">${timestamp}</span>
            </div>
            <div class="message-content">${this.escapeHtml(message.content)}</div>
        `;
        
        return messageDiv;
    }
    
    clearMessages() {
        document.getElementById('messages-list').innerHTML = '';
    }
    
    setLoading(loading) {
        this.isLoading = loading;
        const indicator = document.getElementById('loading-indicator');
        indicator.classList.toggle('hidden', !loading);
    }
    
    setConnectionStatus(status) {
        const statusElement = document.getElementById('connection-status');
        statusElement.textContent = status;
        statusElement.className = `connection-status ${status}`;
    }
    
    showTypingIndicator(username) {
        this.typingUsers.add(username);
        this.updateTypingIndicator();
        
        // Clear typing indicator after 3 seconds
        setTimeout(() => {
            this.typingUsers.delete(username);
            this.updateTypingIndicator();
        }, 3000);
    }
    
    updateTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        const textElement = document.getElementById('typing-text');
        
        if (this.typingUsers.size === 0) {
            indicator.classList.add('hidden');
        } else {
            const users = Array.from(this.typingUsers);
            let text;
            
            if (users.length === 1) {
                text = `${users[0]} is typing...`;
            } else if (users.length === 2) {
                text = `${users[0]} and ${users[1]} are typing...`;
            } else {
                text = `${users.length} people are typing...`;
            }
            
            textElement.textContent = text;
            indicator.classList.remove('hidden');
        }
    }
    
    handleTyping() {
        // Throttle typing notifications
        if (!this.typingTimeout) {
            this.wsClient.sendTypingNotification();
            this.typingTimeout = setTimeout(() => {
                this.typingTimeout = null;
            }, 1000);
        }
    }
    
    scrollToBottom() {
        const messagesContainer = document.getElementById('chat-messages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    showError(message) {
        // Simple error display - could be enhanced with a proper notification system
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        
        this.container.appendChild(errorDiv);
        
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
```

#### 4. Main Application Integration
```javascript
// frontend/js/main.js
class GameApplication {
    constructor() {
        this.authToken = localStorage.getItem('authToken');
        this.apiClient = new ChatAPIClient('http://localhost:8000/api', this.authToken);
        this.wsClient = new ChatWebSocketClient('ws://localhost:8000/api', this.authToken);
        
        this.initializeChat();
    }
    
    initializeChat() {
        // Initialize chat component
        this.chatComponent = new ChatComponent('chat-container', this.apiClient, this.wsClient);
        
        // Handle authentication changes
        window.addEventListener('authTokenChanged', (event) => {
            this.authToken = event.detail.token;
            this.apiClient.authToken = this.authToken;
            this.wsClient.authToken = this.authToken;
            localStorage.setItem('authToken', this.authToken);
        });
        
        // Handle logout
        window.addEventListener('logout', () => {
            this.wsClient.disconnect();
            localStorage.removeItem('authToken');
        });
    }
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (localStorage.getItem('authToken')) {
        new GameApplication();
    } else {
        // Redirect to login or show login form
        console.log('No auth token found, please log in');
    }
});
```

## Key Improvements in Separated Architecture

### 1. **Separation of Concerns**
- **Backend**: Handles business logic, validation, persistence, and security
- **Frontend**: Handles UI, user interactions, and presentation

### 2. **Real-time Communication**
- WebSocket connection for instant message delivery
- Typing indicators and user presence
- Automatic reconnection handling

### 3. **Scalability**
- Stateless API endpoints
- Connection pooling for WebSockets
- Rate limiting and validation

### 4. **Security**
- Server-side validation and profanity filtering
- JWT-based authentication
- Rate limiting to prevent spam

### 5. **User Experience**
- Immediate UI feedback
- Progressive loading of message history
- Offline-capable design patterns

### 6. **Maintainability**
- Clear API contracts
- Modular frontend components
- Comprehensive error handling

## Running the Example

### Backend Setup
```bash
# Install dependencies
pip install fastapi uvicorn sqlalchemy sqlite3

# Run the server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
# Serve static files (simple Python server)
cd frontend
python -m http.server 8080

# Or with Node.js
npx serve .
```

### Testing
```bash
# Backend tests
pytest backend/tests/

# Frontend tests (if using Jest)
npm test
```

This example demonstrates a complete transformation from a monolithic chat system to a modern, scalable architecture with clear separation between backend and frontend responsibilities.

## Next Steps

1. Review [Testing and Integration Strategy](./06-testing-integration.md) for comprehensive testing approaches
2. Implement similar patterns for other game features (inventory, quests, etc.)
3. Consider adding more advanced features like message encryption, file uploads, or voice chat