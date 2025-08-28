# Sample Code Conversion Examples

This directory contains before/after examples showing how to convert monolithic game code into a separated backend/frontend architecture.

## Examples Included

### 1. Character Creation System
- **before/**: Monolithic character creation with mixed UI/logic
- **after/**: Separated backend service + frontend component

### 2. Chat System
- **before/**: Mixed chat system with HTML generation in backend
- **after/**: WebSocket-based real-time chat with API

### 3. Inventory Management
- **before/**: Server-side inventory UI generation
- **after/**: REST API + interactive frontend

### 4. Quest System
- **before/**: Monolithic quest management
- **after/**: Microservice-style quest API + UI

## Key Patterns Demonstrated

### Backend Separation
- Business logic moved to service layer
- Data validation on server side
- API endpoint creation
- WebSocket event handling

### Frontend Separation  
- UI components with clear responsibilities
- Client-side state management
- API communication patterns
- Real-time WebSocket integration

### Common Improvements
- Better error handling
- Input validation on both sides
- Performance optimizations
- Security enhancements

## Usage

Each example includes:
1. **Original Code**: The monolithic version
2. **Converted Code**: Backend and frontend separated
3. **Migration Notes**: Step-by-step conversion process
4. **Benefits**: What was gained from the conversion

## Lessons Learned

### What to Keep on Backend
- Game logic and rules
- Data validation
- Security checks
- Database operations

### What to Move to Frontend
- UI interactions
- Visual feedback
- Client-side caching
- User experience enhancements

### What to Handle on Both
- Input validation (UX on frontend, security on backend)
- Error handling (user-friendly messages on frontend, logging on backend)
- State management (UI state on frontend, game state on backend)