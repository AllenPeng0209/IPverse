# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Jaaz is an open-source multimodal creative assistant - an alternative to Canva that runs locally or with cloud APIs. It's an Electron-based desktop application with a React frontend, Python FastAPI backend, and canvas-based design interface.

**Key Features:**
- Canvas-based design with drag-and-drop interface using Excalidraw
- Multi-modal AI agents for text, image, and video generation
- Support for local models (Ollama, ComfyUI) and cloud APIs (OpenAI, Claude, Replicate)
- Real-time collaboration via WebSocket
- LangGraph-based agent orchestration
- Extensible tool system with provider abstraction

## Architecture

### Frontend (React + Electron)
- **Location:** `react/` (React UI) + `electron/` (Electron main process)
- **Framework:** React 19 with Vite, TypeScript, TailwindCSS
- **Router:** TanStack Router with file-based routing in `react/src/routes/`
- **State:** Zustand stores in `react/src/stores/`
- **Canvas:** Excalidraw integration for infinite canvas design
- **I18n:** react-i18next with locales in `react/src/i18n/locales/`

### Backend (Python FastAPI)
- **Location:** `server/`
- **Framework:** FastAPI with WebSocket support
- **Database:** SQLite with async operations (aiosqlite)
- **Architecture:** Service-oriented with clear separation of concerns

#### Service Architecture
- **ConfigService:** TOML-based configuration management for providers and models
- **DatabaseService:** SQLite persistence with migration support
- **ChatService:** Chat request handling and session management  
- **LangGraphService:** Multi-agent orchestration using LangGraph
- **ToolService:** Dynamic tool registry supporting multiple AI providers
- **WebSocketService:** Real-time communication between frontend/backend
- **JaazService:** Cloud API integration for Jaaz-specific services

### Key Directories
- **Components:** `react/src/components/` - UI components organized by feature
- **API Layer:** `react/src/api/` - Frontend API clients
- **Backend Routes:** `server/routers/` - FastAPI route handlers
- **Tools:** `server/tools/` - AI generation tools for various providers
- **Services:** `server/services/` - Core business logic services

## Development Commands

### Frontend Development
```bash
cd react
npm install --force
npm run dev              # Start Vite dev server
npm run build           # Build for production
npm run lint            # Run ESLint
```

### Backend Development  
```bash
cd server
pip install -r requirements.txt
python main.py          # Start FastAPI server (port 8686)
```

### Full Application
```bash
# Development mode (both frontend and backend)
npm run dev

# Production build
npm run start           # Build React + start Electron

# Electron builds
npm run build:mac       # macOS build
npm run build:win       # Windows build  
npm run build:linux     # Linux build
```

### Testing
```bash
npm test               # Run Vitest tests
npm run test:run       # Run tests once
npm run test:watch     # Watch mode
```

### Code Quality
```bash
# Frontend
cd react && npm run lint

# Backend (Python formatting)
cd server
black .                # Format with Black
ruff check .           # Lint with Ruff
```

## Configuration

### Python Configuration
- **Format:** TOML configuration in `pyproject.toml`
- **Formatting:** Black (line length 88) + Ruff linting
- **Python Version:** >= 3.12 required

### TypeScript Configuration
- **Files:** `react/tsconfig.json`, `electron/tsconfig.json`  
- **ESLint:** `react/eslint.config.js` with React hooks + TypeScript rules
- **Build:** Vite for React, TypeScript compiler for Electron

## Key Integration Points

### Canvas System
- Uses Excalidraw for infinite canvas interface
- Canvas state managed in `react/src/stores/canvas.ts`
- Backend canvas operations in `server/routers/canvas.py`

### AI Tool System
- Tool registration in `server/services/tool_service.py`
- Provider-specific tools in `server/tools/` by provider type
- Dynamic tool loading based on configuration

### WebSocket Communication
- Real-time updates between frontend and backend
- Session-based message broadcasting
- Event-driven architecture for chat and canvas updates

### Multi-Provider Support
- Unified interface for different AI providers (OpenAI, Ollama, Jaaz, Replicate)
- Configuration-driven provider selection
- Extensible tool system supporting custom workflows

## Development Notes

- The application requires Python >= 3.12
- Use `npm install --force` for React dependencies due to peer dependency conflicts
- Backend runs on port 8686, frontend dev server on port 5173
- Database migrations are handled automatically via the migration system
- ComfyUI integration requires separate ComfyUI installation for local workflows