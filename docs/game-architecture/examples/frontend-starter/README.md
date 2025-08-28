# Game Frontend Starter

A complete JavaScript frontend for game development with modular architecture, real-time features, and responsive design.

## Features

- Vanilla JavaScript with ES6+ modules
- Responsive CSS Grid/Flexbox layout
- WebSocket real-time communication
- Component-based architecture
- Local state management
- Authentication system
- Chat functionality
- Character management

## Quick Start

```bash
# Option 1: Simple HTTP server (Python)
python -m http.server 8080

# Option 2: Node.js serve
npx serve .

# Option 3: PHP built-in server
php -S localhost:8080

# Open browser to: http://localhost:8080
```

## Project Structure

```
frontend-starter/
├── index.html              # Main HTML file
├── css/
│   ├── main.css           # Main styles
│   ├── components.css     # Component styles
│   └── responsive.css     # Responsive styles
├── js/
│   ├── main.js           # Application entry point
│   ├── api-client.js     # API communication
│   ├── websocket-client.js # WebSocket handling
│   ├── auth.js           # Authentication logic
│   └── state-manager.js  # State management
├── components/
│   ├── auth-component.js     # Login/register
│   ├── character-component.js # Character management
│   ├── chat-component.js     # Chat interface
│   └── inventory-component.js # Inventory management
├── assets/
│   ├── images/           # Game images
│   └── sounds/           # Sound effects
└── tests/
    ├── unit/             # Unit tests
    └── e2e/              # End-to-end tests
```

## Configuration

Update `js/config.js`:

```javascript
const CONFIG = {
    API_BASE_URL: 'http://localhost:8000/api',
    WS_BASE_URL: 'ws://localhost:8000/api',
    ENABLE_DEBUGGING: true,
    CACHE_DURATION: 5 * 60 * 1000 // 5 minutes
};
```

## Components

### Authentication Component
- User registration and login
- Token management
- Protected route handling

### Character Component
- Character creation and selection
- Character stats display
- Character customization

### Chat Component
- Real-time messaging
- Channel selection
- Typing indicators
- Message history

### Inventory Component
- Item display and management
- Drag and drop interface
- Equipment slots

## Features

### Real-time Communication
- WebSocket connection management
- Automatic reconnection
- Event-driven architecture

### State Management
- Centralized application state
- Event bus for component communication
- Local storage persistence

### Responsive Design
- Mobile-first approach
- Grid-based layout
- Touch-friendly interfaces

## Development

### Adding New Components

1. Create component file in `components/`
2. Import in `main.js`
3. Add corresponding CSS in `css/components.css`
4. Add tests in `tests/unit/`

### API Integration

All API calls go through `js/api-client.js`:

```javascript
// Example usage
const apiClient = new GameAPIClient();
const characters = await apiClient.getCharacters();
```

### WebSocket Usage

WebSocket events are handled through `js/websocket-client.js`:

```javascript
// Example usage
const wsClient = new WebSocketClient();
wsClient.on('chat_message', handleNewMessage);
wsClient.connect(channelId);
```

## Testing

### Unit Tests (Jest)
```bash
npm install
npm test
```

### E2E Tests (Cypress)
```bash
npm run test:e2e
```

## Browser Support

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Performance

- Lazy loading for components
- Image optimization
- Minimal dependencies
- Efficient state updates

## Deployment

### Static Hosting
Upload all files to any static hosting service (Netlify, Vercel, GitHub Pages, etc.)

### CDN Configuration
For production, consider using a CDN for assets and enabling compression.

### Environment Configuration
Update API URLs for production in `js/config.js`