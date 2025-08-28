# Code Conversion Mapping

## Overview

This document provides guidance on analyzing existing code and determining what logic should remain in the backend versus what can/should be moved to the JavaScript frontend. It includes practical examples and modularization strategies.

## Analysis Framework

### Backend Logic (Keep on Server)
These components should **always** remain on the backend:

1. **Business Rules & Game Logic**
   - Combat calculations
   - Experience point calculations
   - Item drop rates and probability
   - Quest progression logic
   - Economic systems (pricing, trading)

2. **Data Integrity & Validation**
   - Player data validation
   - Anti-cheat mechanisms
   - Resource constraints enforcement
   - Permission checking

3. **Persistent Data Management**
   - Database operations
   - File system operations
   - User authentication
   - Session management

4. **Security-Critical Operations**
   - Password handling
   - Payment processing
   - Admin functions
   - Sensitive calculations

### Frontend Logic (Move to Client)
These components can be safely moved to the frontend:

1. **User Interface Logic**
   - Form validation (with backend verification)
   - UI state management
   - Visual effects and animations
   - User preference handling

2. **Presentation Layer**
   - Data formatting and display
   - Sorting and filtering (for display)
   - Client-side routing
   - Theme and appearance settings

3. **Performance Optimizations**
   - Client-side caching
   - Predictive loading
   - Local state management
   - Debouncing and throttling

4. **User Experience Features**
   - Auto-complete functionality
   - Real-time input validation
   - Offline capabilities
   - Progressive enhancement

## Sample Code Analysis

### Example 1: Character Creation System

#### Original Monolithic Code (Python)
```python
class CharacterCreationSystem:
    def __init__(self):
        self.db = DatabaseConnection()
        self.validator = CharacterValidator()
    
    def create_character_form(self):
        """Generates HTML form for character creation"""
        # Frontend logic mixed with backend
        html = """
        <form id="char-form">
            <input type="text" name="name" placeholder="Character Name">
            <select name="class">
                <option value="warrior">Warrior</option>
                <option value="mage">Mage</option>
            </select>
            <button type="submit">Create Character</button>
        </form>
        """
        return html
    
    def validate_character_data(self, data):
        """Validates character creation data"""
        # This should stay on backend
        if not data.get('name') or len(data['name']) < 3:
            return False, "Name must be at least 3 characters"
        
        if data.get('class') not in ['warrior', 'mage', 'rogue']:
            return False, "Invalid character class"
        
        # Check for duplicate names
        if self.db.character_exists(data['name']):
            return False, "Character name already exists"
        
        return True, "Valid"
    
    def calculate_starting_stats(self, character_class):
        """Calculates starting attributes based on class"""
        # This should stay on backend
        base_stats = {'warrior': {'str': 16, 'int': 8, 'dex': 12}}
        return base_stats.get(character_class, {})
    
    def save_character(self, data):
        """Saves character to database"""
        # This should stay on backend
        is_valid, message = self.validate_character_data(data)
        if not is_valid:
            return {'success': False, 'error': message}
        
        stats = self.calculate_starting_stats(data['class'])
        character = {
            'name': data['name'],
            'class': data['class'],
            'stats': stats,
            'level': 1,
            'experience': 0
        }
        
        character_id = self.db.insert_character(character)
        return {'success': True, 'character_id': character_id}
```

#### Separated Architecture

**Backend (Python) - Keep Business Logic:**
```python
# backend/services/character_service.py
class CharacterService:
    def __init__(self, db):
        self.db = db
    
    def validate_character_data(self, data):
        """Server-side validation - KEEP ON BACKEND"""
        if not data.get('name') or len(data['name']) < 3:
            raise ValidationError("Name must be at least 3 characters")
        
        if data.get('class') not in ['warrior', 'mage', 'rogue']:
            raise ValidationError("Invalid character class")
        
        if self.db.character_exists(data['name']):
            raise ValidationError("Character name already exists")
    
    def calculate_starting_stats(self, character_class):
        """Game logic calculation - KEEP ON BACKEND"""
        base_stats = {
            'warrior': {'strength': 16, 'intelligence': 8, 'dexterity': 12},
            'mage': {'strength': 8, 'intelligence': 16, 'dexterity': 10},
            'rogue': {'strength': 10, 'intelligence': 12, 'dexterity': 16}
        }
        return base_stats.get(character_class, {})
    
    def create_character(self, user_id, data):
        """Character creation business logic - KEEP ON BACKEND"""
        self.validate_character_data(data)
        
        stats = self.calculate_starting_stats(data['class'])
        character = {
            'user_id': user_id,
            'name': data['name'],
            'class': data['class'],
            'stats': stats,
            'level': 1,
            'experience': 0,
            'health': 100,
            'mana': 50
        }
        
        return self.db.create_character(character)

# backend/api/character_routes.py
from fastapi import APIRouter, HTTPException, Depends
from .auth import get_current_user
from .models import CharacterCreateRequest

router = APIRouter()

@router.post("/characters")
async def create_character(
    request: CharacterCreateRequest,
    current_user = Depends(get_current_user),
    character_service = Depends(get_character_service)
):
    try:
        character = character_service.create_character(
            current_user.id, 
            request.dict()
        )
        return {"success": True, "data": character}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

**Frontend (JavaScript) - Handle UI and UX:**
```javascript
// frontend/components/CharacterCreation.js
class CharacterCreation {
    constructor() {
        this.apiClient = new GameAPIClient();
        this.validator = new ClientValidator();
        this.setupForm();
    }
    
    setupForm() {
        // UI logic - MOVE TO FRONTEND
        const form = document.getElementById('character-form');
        form.addEventListener('submit', this.handleSubmit.bind(this));
        
        // Real-time validation feedback - MOVE TO FRONTEND
        const nameInput = document.getElementById('name');
        nameInput.addEventListener('input', this.validateNameInput.bind(this));
    }
    
    validateNameInput(event) {
        // Client-side validation for UX - MOVE TO FRONTEND
        const name = event.target.value;
        const feedback = document.getElementById('name-feedback');
        
        if (name.length < 3) {
            feedback.textContent = 'Name must be at least 3 characters';
            feedback.className = 'error';
        } else {
            feedback.textContent = 'Name looks good!';
            feedback.className = 'success';
        }
    }
    
    async handleSubmit(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const characterData = {
            name: formData.get('name'),
            class: formData.get('class')
        };
        
        // Client-side validation - MOVE TO FRONTEND
        if (!this.validator.validateCharacterData(characterData)) {
            this.showError('Please fix the errors before submitting');
            return;
        }
        
        try {
            // API call to backend - KEEP AS API CALL
            const response = await this.apiClient.createCharacter(characterData);
            this.handleSuccess(response.data);
        } catch (error) {
            this.handleError(error.message);
        }
    }
    
    showPreview(characterClass) {
        // Visual preview - MOVE TO FRONTEND
        const preview = document.getElementById('character-preview');
        const stats = this.getPreviewStats(characterClass);
        
        preview.innerHTML = `
            <h3>Starting Stats Preview</h3>
            <div>Strength: ${stats.strength}</div>
            <div>Intelligence: ${stats.intelligence}</div>
            <div>Dexterity: ${stats.dexterity}</div>
        `;
    }
    
    getPreviewStats(characterClass) {
        // Static data for preview - MOVE TO FRONTEND
        const previewStats = {
            'warrior': {strength: 16, intelligence: 8, dexterity: 12},
            'mage': {strength: 8, intelligence: 16, dexterity: 10},
            'rogue': {strength: 10, intelligence: 12, dexterity: 16}
        };
        return previewStats[characterClass] || {};
    }
}
```

### Example 2: Quest Management System

#### Original Monolithic Code
```python
class QuestManager:
    def display_quest_board(self, player_level):
        # Mixed UI and business logic
        available_quests = self.get_available_quests(player_level)
        html = "<div class='quest-board'>"
        for quest in available_quests:
            if self.can_player_accept_quest(quest, player_level):
                html += f"<div class='quest'>{quest.title}</div>"
        html += "</div>"
        return html
    
    def get_available_quests(self, player_level):
        # Business logic - should stay on backend
        return self.db.get_quests_for_level(player_level)
    
    def accept_quest(self, player_id, quest_id):
        # Business logic - should stay on backend
        quest = self.db.get_quest(quest_id)
        if not self.can_player_accept_quest(quest, player_id):
            return False
        return self.db.assign_quest_to_player(player_id, quest_id)
```

#### Separated Architecture

**Backend (Python):**
```python
# backend/services/quest_service.py
class QuestService:
    def get_available_quests(self, player_level, filters=None):
        """Get quests appropriate for player - KEEP ON BACKEND"""
        quests = self.db.get_quests_by_level_range(
            min_level=max(1, player_level - 2),
            max_level=player_level + 1
        )
        
        if filters:
            quests = self.apply_filters(quests, filters)
        
        return [self.format_quest_data(q) for q in quests]
    
    def can_accept_quest(self, player_id, quest_id):
        """Business rule validation - KEEP ON BACKEND"""
        player = self.db.get_player(player_id)
        quest = self.db.get_quest(quest_id)
        
        # Check level requirements
        if player.level < quest.min_level:
            return False, "Level too low"
        
        # Check prerequisites
        if not self.has_prerequisites(player, quest):
            return False, "Missing prerequisites"
        
        # Check if already completed
        if self.db.player_completed_quest(player_id, quest_id):
            return False, "Quest already completed"
        
        return True, "Can accept"
    
    def accept_quest(self, player_id, quest_id):
        """Quest acceptance logic - KEEP ON BACKEND"""
        can_accept, reason = self.can_accept_quest(player_id, quest_id)
        if not can_accept:
            raise QuestError(reason)
        
        return self.db.create_quest_instance(player_id, quest_id)
```

**Frontend (JavaScript):**
```javascript
// frontend/components/QuestBoard.js
class QuestBoard {
    constructor() {
        this.apiClient = new GameAPIClient();
        this.quests = [];
        this.filters = {
            difficulty: 'all',
            type: 'all',
            rewards: 'all'
        };
        this.setupEventListeners();
    }
    
    async loadQuests() {
        try {
            const response = await this.apiClient.getAvailableQuests();
            this.quests = response.data.quests;
            this.renderQuestBoard();
        } catch (error) {
            this.showError('Failed to load quests');
        }
    }
    
    renderQuestBoard() {
        // UI rendering - MOVE TO FRONTEND
        const board = document.getElementById('quest-board');
        const filteredQuests = this.filterQuests(this.quests);
        
        board.innerHTML = filteredQuests.map(quest => 
            this.renderQuestCard(quest)
        ).join('');
        
        this.attachQuestEventListeners();
    }
    
    filterQuests(quests) {
        // Client-side filtering for UI - MOVE TO FRONTEND
        return quests.filter(quest => {
            if (this.filters.difficulty !== 'all' && 
                quest.difficulty !== this.filters.difficulty) {
                return false;
            }
            if (this.filters.type !== 'all' && 
                quest.type !== this.filters.type) {
                return false;
            }
            return true;
        });
    }
    
    renderQuestCard(quest) {
        // UI template - MOVE TO FRONTEND
        return `
            <div class="quest-card" data-quest-id="${quest.quest_id}">
                <h3>${quest.title}</h3>
                <p class="difficulty ${quest.difficulty}">${quest.difficulty.toUpperCase()}</p>
                <p class="description">${quest.description}</p>
                <div class="rewards">
                    <span>XP: ${quest.rewards.experience}</span>
                    <span>Gold: ${quest.rewards.gold}</span>
                </div>
                <button class="accept-quest-btn">Accept Quest</button>
            </div>
        `;
    }
    
    async acceptQuest(questId) {
        try {
            // Show loading state - FRONTEND
            this.showQuestLoading(questId);
            
            // API call to backend - KEEP AS API CALL
            const response = await this.apiClient.acceptQuest(questId);
            
            // Update UI - FRONTEND
            this.showQuestAccepted(questId);
            this.updateActiveQuests(response.data);
            
        } catch (error) {
            this.showQuestError(questId, error.message);
        }
    }
}
```

## Modularization Strategy

### 1. Service Layer Separation

**Backend Services:**
```python
# backend/services/
├── character_service.py    # Character business logic
├── quest_service.py       # Quest business logic
├── inventory_service.py   # Inventory management
├── chat_service.py        # Chat moderation and persistence
└── auth_service.py        # Authentication and authorization
```

**Frontend Services:**
```javascript
// frontend/services/
├── api-client.js          # API communication
├── websocket-client.js    # Real-time communication
├── cache-service.js       # Client-side caching
├── ui-state-manager.js    # UI state management
└── validator.js           # Client-side validation
```

### 2. Data Flow Architecture

```
Frontend                    Backend
┌─────────────────┐        ┌─────────────────┐
│   UI Components │        │   API Routes    │
│   ↓             │        │   ↓             │
│   State Manager │◄──────►│   Controllers   │
│   ↓             │        │   ↓             │
│   API Client    │        │   Services      │
│                 │        │   ↓             │
│                 │        │   Data Models   │
│                 │        │   ↓             │
│                 │        │   Database      │
└─────────────────┘        └─────────────────┘
```

### 3. Shared Code Patterns

**Configuration and Constants:**
```javascript
// shared/constants.js (can be used by both frontend and backend)
export const CHARACTER_CLASSES = {
    WARRIOR: 'warrior',
    MAGE: 'mage',
    ROGUE: 'rogue'
};

export const VALIDATION_RULES = {
    CHARACTER_NAME: {
        MIN_LENGTH: 3,
        MAX_LENGTH: 20,
        PATTERN: /^[a-zA-Z0-9_]+$/
    }
};
```

## Migration Checklist

### Phase 1: Identify Components
- [ ] List all current functions/classes
- [ ] Categorize each as frontend/backend/shared
- [ ] Identify dependencies between components
- [ ] Plan migration order

### Phase 2: Extract Backend Logic
- [ ] Create service layer for business logic
- [ ] Implement API endpoints
- [ ] Add validation and error handling
- [ ] Set up data access layer

### Phase 3: Create Frontend Components
- [ ] Build UI components
- [ ] Implement API client
- [ ] Add client-side state management
- [ ] Create user interaction handlers

### Phase 4: Integration
- [ ] Connect frontend to backend APIs
- [ ] Test data flow between layers
- [ ] Implement error handling
- [ ] Add loading states and feedback

## Best Practices

### 1. Keep Security on Backend
```python
# GOOD - Backend validation
def transfer_gold(from_player, to_player, amount):
    if from_player.gold < amount:
        raise InsufficientFundsError()
    # Process transfer...

# BAD - Frontend only validation
# JavaScript: if (player.gold >= amount) { /* transfer */ }
```

### 2. Optimize User Experience with Frontend
```javascript
// GOOD - Immediate feedback with backend verification
async function validateUsername(username) {
    // Immediate client-side check
    if (username.length < 3) {
        showError("Username too short");
        return false;
    }
    
    // Backend verification
    const available = await api.checkUsernameAvailability(username);
    if (!available) {
        showError("Username not available");
        return false;
    }
    
    showSuccess("Username available");
    return true;
}
```

### 3. Handle Sensitive Data Properly
```python
# GOOD - Sensitive calculations on backend
def calculate_damage(attacker, defender, weapon):
    base_damage = weapon.damage
    modifier = attacker.strength / 10
    defense = defender.armor_value
    return max(1, base_damage + modifier - defense)

# BAD - Sensitive calculations on frontend
# This could be manipulated by cheaters
```

## Next Steps

1. Review the [Migration Plan](./04-migration-plan.md) for step-by-step implementation
2. See [Chat Example](./05-chat-example.md) for complete conversion example
3. Check [Testing Strategy](./06-testing-integration.md) for validation approaches