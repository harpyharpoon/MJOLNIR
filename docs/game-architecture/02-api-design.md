# REST API Design

## Overview

This document provides a comprehensive REST API schema that allows a JavaScript frontend to interact with a Python backend for game features including character creation, chat messaging, gear management, and quest board management.

## API Design Principles

### RESTful Conventions
- Use HTTP methods appropriately (GET, POST, PUT, DELETE)
- Resource-based URLs
- Consistent response formats
- Proper HTTP status codes

### Response Format
All API responses follow this structure:
```json
{
  "success": true,
  "data": {},
  "message": "Operation successful",
  "timestamp": "2025-01-01T10:00:00Z"
}
```

## Authentication Endpoints

### POST /api/auth/login
Authenticate user and receive JWT token.

**Request:**
```json
{
  "username": "player123",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "user_123",
      "username": "player123",
      "role": "player"
    }
  },
  "message": "Login successful"
}
```

### POST /api/auth/register
Register new user account.

**Request:**
```json
{
  "username": "newplayer",
  "email": "player@email.com",
  "password": "secure_password"
}
```

## Character Management

### POST /api/characters
Create a new character.

**Request:**
```json
{
  "name": "Thorin Ironbeard",
  "class": "warrior",
  "race": "dwarf",
  "attributes": {
    "strength": 16,
    "dexterity": 12,
    "constitution": 15,
    "intelligence": 10,
    "wisdom": 13,
    "charisma": 8
  },
  "appearance": {
    "hair_color": "brown",
    "eye_color": "blue",
    "height": "4'8\"",
    "weight": "180 lbs"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "character_id": "char_789",
    "name": "Thorin Ironbeard",
    "class": "warrior",
    "race": "dwarf",
    "level": 1,
    "experience": 0,
    "health": 100,
    "mana": 50,
    "attributes": {
      "strength": 16,
      "dexterity": 12,
      "constitution": 15,
      "intelligence": 10,
      "wisdom": 13,
      "charisma": 8
    },
    "location": "starting_village",
    "created_at": "2025-01-01T10:00:00Z"
  },
  "message": "Character created successfully"
}
```

### GET /api/characters
Get all characters for the authenticated user.

**Response:**
```json
{
  "success": true,
  "data": {
    "characters": [
      {
        "character_id": "char_789",
        "name": "Thorin Ironbeard",
        "class": "warrior",
        "level": 5,
        "location": "mountain_pass",
        "health": 85,
        "last_active": "2025-01-01T09:30:00Z"
      }
    ]
  }
}
```

### GET /api/characters/{character_id}
Get detailed character information.

**Response:**
```json
{
  "success": true,
  "data": {
    "character_id": "char_789",
    "name": "Thorin Ironbeard",
    "class": "warrior",
    "race": "dwarf",
    "level": 5,
    "experience": 2450,
    "health": 85,
    "max_health": 120,
    "mana": 30,
    "max_mana": 60,
    "attributes": {
      "strength": 18,
      "dexterity": 13,
      "constitution": 16,
      "intelligence": 10,
      "wisdom": 13,
      "charisma": 9
    },
    "location": "mountain_pass",
    "inventory_slots": 20,
    "guild_id": "guild_456"
  }
}
```

### PUT /api/characters/{character_id}
Update character information.

**Request:**
```json
{
  "location": "forest_clearing",
  "health": 95
}
```

### DELETE /api/characters/{character_id}
Delete a character.

## Chat Messaging

### GET /api/chat/channels
Get available chat channels.

**Response:**
```json
{
  "success": true,
  "data": {
    "channels": [
      {
        "channel_id": "general",
        "name": "General Chat",
        "type": "public",
        "description": "General discussion for all players"
      },
      {
        "channel_id": "guild_456",
        "name": "Iron Warriors",
        "type": "guild",
        "description": "Guild-only communication"
      }
    ]
  }
}
```

### GET /api/chat/channels/{channel_id}/messages
Get chat messages for a channel.

**Query Parameters:**
- `limit`: Number of messages (default: 50, max: 100)
- `before`: Get messages before this timestamp
- `after`: Get messages after this timestamp

**Response:**
```json
{
  "success": true,
  "data": {
    "messages": [
      {
        "message_id": "msg_123",
        "user_id": "user_456",
        "username": "PlayerOne",
        "character_name": "Elara Moonwhisper",
        "content": "Anyone up for a dungeon run?",
        "timestamp": "2025-01-01T10:15:00Z",
        "channel_id": "general"
      }
    ],
    "has_more": true,
    "total_count": 150
  }
}
```

### POST /api/chat/channels/{channel_id}/messages
Send a message to a channel.

**Request:**
```json
{
  "content": "Count me in for the dungeon!",
  "character_id": "char_789"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "message_id": "msg_124",
    "content": "Count me in for the dungeon!",
    "timestamp": "2025-01-01T10:16:00Z",
    "character_name": "Thorin Ironbeard"
  }
}
```

### DELETE /api/chat/messages/{message_id}
Delete a message (admin or message author only).

## Gear/Inventory Management

### GET /api/characters/{character_id}/inventory
Get character's inventory.

**Response:**
```json
{
  "success": true,
  "data": {
    "inventory": {
      "slots_used": 12,
      "slots_total": 20,
      "gold": 1250,
      "items": [
        {
          "item_id": "item_001",
          "name": "Iron Sword",
          "type": "weapon",
          "subtype": "sword",
          "quantity": 1,
          "equipped": true,
          "slot": "main_hand",
          "stats": {
            "damage": "1d8+2",
            "durability": 85
          },
          "rarity": "common",
          "value": 50
        },
        {
          "item_id": "item_002",
          "name": "Health Potion",
          "type": "consumable",
          "quantity": 5,
          "effects": {
            "heal": 25
          },
          "value": 10
        }
      ]
    }
  }
}
```

### POST /api/characters/{character_id}/inventory/items
Add item to inventory.

**Request:**
```json
{
  "item_id": "item_003",
  "quantity": 1,
  "source": "quest_reward"
}
```

### PUT /api/characters/{character_id}/inventory/items/{item_id}
Update item in inventory (e.g., equip/unequip).

**Request:**
```json
{
  "equipped": true,
  "slot": "chest"
}
```

### DELETE /api/characters/{character_id}/inventory/items/{item_id}
Remove item from inventory.

**Query Parameters:**
- `quantity`: Number to remove (optional, defaults to all)

### GET /api/items
Get available items (for shops, crafting, etc.).

**Query Parameters:**
- `type`: Filter by item type
- `rarity`: Filter by rarity
- `level_min`: Minimum required level
- `level_max`: Maximum required level

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "item_id": "item_sword_steel",
        "name": "Steel Sword",
        "type": "weapon",
        "subtype": "sword",
        "rarity": "uncommon",
        "required_level": 10,
        "stats": {
          "damage": "1d8+4",
          "durability": 100
        },
        "price": 200,
        "description": "A well-crafted steel sword with a sharp edge."
      }
    ]
  }
}
```

## Quest Management

### GET /api/quests
Get available quests.

**Query Parameters:**
- `status`: Filter by quest status (available, active, completed)
- `difficulty`: Filter by difficulty level
- `type`: Filter by quest type

**Response:**
```json
{
  "success": true,
  "data": {
    "quests": [
      {
        "quest_id": "quest_001",
        "title": "The Missing Merchant",
        "description": "A local merchant has gone missing while traveling to the next town. Find out what happened to him.",
        "difficulty": "easy",
        "type": "investigation",
        "level_requirement": 3,
        "rewards": {
          "experience": 150,
          "gold": 75,
          "items": ["item_boots_leather"]
        },
        "objectives": [
          {
            "id": "obj_001",
            "description": "Speak with the merchant's wife",
            "completed": false
          },
          {
            "id": "obj_002",
            "description": "Search the road to the next town",
            "completed": false
          }
        ],
        "giver": {
          "npc_id": "npc_mayor",
          "name": "Mayor Aldrich",
          "location": "town_hall"
        },
        "time_limit": null,
        "prerequisites": []
      }
    ]
  }
}
```

### POST /api/characters/{character_id}/quests/{quest_id}/accept
Accept a quest.

**Response:**
```json
{
  "success": true,
  "data": {
    "quest_instance_id": "qi_001",
    "accepted_at": "2025-01-01T10:30:00Z",
    "status": "active"
  }
}
```

### GET /api/characters/{character_id}/quests
Get character's active and completed quests.

**Query Parameters:**
- `status`: Filter by status (active, completed, failed)

**Response:**
```json
{
  "success": true,
  "data": {
    "quests": [
      {
        "quest_instance_id": "qi_001",
        "quest_id": "quest_001",
        "title": "The Missing Merchant",
        "status": "active",
        "progress": {
          "objectives_completed": 1,
          "objectives_total": 2
        },
        "accepted_at": "2025-01-01T10:30:00Z",
        "completed_at": null
      }
    ]
  }
}
```

### PUT /api/characters/{character_id}/quests/{quest_instance_id}/objectives/{objective_id}
Update quest objective progress.

**Request:**
```json
{
  "completed": true,
  "progress_data": {
    "npcs_spoken_to": ["npc_wife"],
    "items_found": []
  }
}
```

### POST /api/characters/{character_id}/quests/{quest_instance_id}/complete
Complete a quest.

**Response:**
```json
{
  "success": true,
  "data": {
    "rewards_granted": {
      "experience": 150,
      "gold": 75,
      "items": ["item_boots_leather"]
    },
    "completed_at": "2025-01-01T11:45:00Z"
  }
}
```

## WebSocket Events

### Real-time Communication
For real-time features, use WebSocket connections at `/ws` with these event types:

#### Chat Events
```json
{
  "type": "chat_message",
  "data": {
    "channel_id": "general",
    "message": "Hello everyone!",
    "character_id": "char_789"
  }
}
```

#### Game State Updates
```json
{
  "type": "character_update",
  "data": {
    "character_id": "char_789",
    "updates": {
      "health": 85,
      "location": "forest_clearing"
    }
  }
}
```

#### Quest Updates
```json
{
  "type": "quest_progress",
  "data": {
    "quest_instance_id": "qi_001",
    "objective_id": "obj_001",
    "completed": true
  }
}
```

## Error Handling

### Standard Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid character data provided",
    "details": {
      "field": "attributes.strength",
      "reason": "Value must be between 1 and 20"
    }
  },
  "timestamp": "2025-01-01T10:00:00Z"
}
```

### Common Error Codes
- `AUTHENTICATION_REQUIRED`: User must be authenticated
- `AUTHORIZATION_FAILED`: User lacks permission for action
- `VALIDATION_ERROR`: Request data is invalid
- `RESOURCE_NOT_FOUND`: Requested resource doesn't exist
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `SERVER_ERROR`: Internal server error

## Rate Limiting

### Standard Limits
- Authentication endpoints: 5 requests per minute
- Chat messages: 30 messages per minute
- General API: 100 requests per minute
- WebSocket connections: 1 per user

### Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Implementation Examples

See the [Chat Broadcasting Example](./05-chat-example.md) for complete backend and frontend implementation of the chat messaging API.

## Next Steps

1. Review the [Code Conversion Mapping](./03-code-conversion-mapping.md) to understand how to structure your code
2. Check the [Migration Plan](./04-migration-plan.md) for implementation strategy
3. See [Testing Strategy](./06-testing-integration.md) for API testing approaches