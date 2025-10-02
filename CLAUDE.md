# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a React-based AI assistant application that simulates an agentic voice assistant integrating multiple AI technologies including Liquid Audio, LM Studio, Memento, LangChain, and N8N. The application provides a chat interface with voice capabilities, memory management, and workflow automation.

## Architecture

The application follows a component-based architecture with:

- **Main Components**: `App.tsx` (root component), `Header.tsx`, `ChatWindow.tsx`, `Sidebar.tsx`, `Footer.tsx`, `SettingsModal.tsx`
- **Services**: `geminiService.ts` for AI model communication and function calling
- **Type Definitions**: `types.ts` for TypeScript interfaces and `constants.ts` for initial data
- **Build System**: Vite with React plugin and TypeScript configuration

## Key Technologies

- **Frontend**: React 19.2.0 with TypeScript and Tailwind CSS
- **AI Integration**: Google Gemini API via @google/genai package
- **Build Tool**: Vite 6.2.0 with React plugin
- **Styling**: Tailwind CSS via CDN and Font Awesome for icons

## Development Commands

```bash
# Install dependencies
npm install

# Start development server (runs on port 3000)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Environment Configuration

The application requires environment variables for AI API access:
- `GEMINI_API_KEY`: Google Gemini API key (required)
- `GEMINI_API_KEY` is also available as `API_KEY` in the build configuration

**Note**: The application expects a `.env.local` file for local development. The Vite configuration injects the API key as `process.env.API_KEY`.

## Core Features

### Multi-LLM Provider Support
- **LM Studio**: Local model hosting with dynamic model loading
- **OpenRouter**: Cloud-based LLM provider with API key authentication

### Agentic Capabilities
- **Function Calling**: Integrated N8N workflow execution via Gemini's function calling
- **Memory System**: Simulated Mento memory integration with context persistence
- **Workflow Orchestration**: LangGraph-style step visualization and state management

### Voice Integration
- **Microphone Access**: Voice input capabilities (requires browser permissions)
- **Audio Processing**: Liquid Audio simulation for voice-based interactions

## File Structure

```
liquid-audio-agent/
├── App.tsx                    # Main application component
├── index.tsx                  # React root renderer
├── index.html                 # HTML entry point with CDN resources
├── types.ts                   # TypeScript type definitions
├── constants.ts               # Application constants and initial data
├── vite.config.ts            # Vite configuration with environment setup
├── tsconfig.json             # TypeScript configuration
├── services/
│   └── geminiService.ts      # Gemini API service with function calling
├── components/
│   ├── Header.tsx            # Application header with status indicators
│   ├── ChatWindow.tsx        # Chat interface and message display
│   ├── Sidebar.tsx           # Model selection and settings panel
│   ├── Footer.tsx            # Application footer
│   └── SettingsModal.tsx     # Configuration modal
├── package.json              # Dependencies and scripts
└── metadata.json             # Project metadata and permissions
```

## Configuration

### Vite Configuration (`vite.config.ts`)
- Development server: `localhost:3000`
- Path alias: `@/` points to project root
- Environment variable injection for API keys

### TypeScript Configuration (`tsconfig.json`)
- Target: ES2022 with experimental decorators
- Module resolution: Bundler mode
- React JSX: React-jsx transform
- Path mapping: `@/*` resolves to project root

## Key Implementation Details

### State Management
- React hooks for component state management
- Centralized state in `App.tsx` with prop drilling to components
- Message history, model selection, and connection settings managed globally

### API Integration
- Gemini API handles both text generation and function calling
- N8N workflow execution through tool calling interface
- Dynamic model loading from LM Studio endpoints

### Component Architecture
- Modular component design with clear separation of concerns
- Event handling for user interactions and real-time updates
- Responsive design with Tailwind CSS classes

## Development Notes

- The application simulates integration with various AI services but primarily uses Google Gemini API
- Voice processing is simulated through browser microphone access
- Memory and workflow state are maintained in component state rather than external services
- Function calling is implemented through Gemini's tool system with custom function declarations