# AI Agent Development Tutor - ChatGPT App

This is the ChatGPT app component of the Course Companion FTE - Hackathon IV project. It serves as an educational tutor that helps students master AI Agent development using Claude Agent SDK, MCP integration, and production deployment patterns.

## Overview

The AI Agent Development Tutor is designed to work with OpenAI's ChatGPT Custom GPT functionality. It integrates with the backend API to provide:

- **Concept Explanations**: Detailed explanations of AI Agent concepts
- **Quiz Sessions**: Interactive quizzes to test knowledge
- **Progress Tracking**: Monitor learning progress and achievements
- **Socratic Tutoring**: Guided learning through strategic questioning

## Architecture

The app follows a Zero-Backend-LLM architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                     ChatGPT Plus/Team                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Custom GPT: Course Companion             │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │              System Instructions                │  │  │
│  │  │  - Educational Persona                          │  │  │
│  │  │  - 4 Agent Skills                               │  │  │
│  │  │  - Course Context                               │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │              Actions (API Integration)          │  │  │
│  │  │  - Content Delivery API                         │  │  │
│  │  │  - Navigation API                               │  │  │
│  │  │  - Quiz API                                     │  │  │
│  │  │  - Progress API                                 │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ REST API Calls
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Backend API (Zero-LLM)                     │
│  - Serves content verbatim                                  │
│  - Grades quizzes deterministically                         │
│  - Tracks progress with SQL                                 │
│  - NO LLM processing                                        │
└─────────────────────────────────────────────────────────────┘
```

## Files

- `config.json`: Main configuration for the ChatGPT app
- `action_manifest.json`: OpenAPI schema defining the API endpoints
- `skill_routing.py`: (Future) Logic for determining which skill to activate based on user input
- `README.md`: This file

## Setup

1. Register the ChatGPT app in the OpenAI GPT Store
2. Configure the API endpoints to point to your deployed backend
3. Set up OAuth authentication with the backend API
4. Test all four skills to ensure proper functionality

## Skills

The app implements four core educational skills:

### 1. Concept Explainer
- **Triggers**: "explain", "what is", "how does", "define"
- **Function**: Provides detailed explanations of AI Agent concepts using course content

### 2. Quiz Master
- **Triggers**: "quiz", "test me", "practice", "assess my knowledge"
- **Function**: Conducts interactive quiz sessions with immediate feedback

### 3. Socratic Tutor
- **Triggers**: "help me think", "guide me", "I'm stuck", "don't give me the answer"
- **Function**: Guides learning through strategic questioning without providing direct answers

### 4. Progress Motivator
- **Triggers**: "my progress", "how am I doing", "streak", "achievements"
- **Function**: Displays learning progress and motivates continued study

## API Endpoints

The app integrates with the backend API through the following endpoints:

### Content Delivery
- `GET /chapters/{chapter_id}`: Retrieve chapter content
- `GET /chapters`: List all chapters
- `GET /modules/{module_id}`: Get module overview

### Navigation
- `GET /chapters/{chapter_id}/next`: Get next chapter
- `GET /navigation/sequence`: Get full chapter sequence

### Quizzes
- `GET /quizzes`: List available quizzes
- `GET /quizzes/{quiz_id}`: Get quiz questions
- `POST /quizzes/{quiz_id}/submit`: Submit quiz answers

### Progress Tracking
- `GET /progress/{user_id}`: Get user progress
- `PUT /progress/{user_id}/chapters/{chapter_id}`: Mark chapter complete
- `GET /progress/{user_id}/streak`: Get learning streak
- `GET /progress/{user_id}/achievements`: Get achievements

## Authentication

The app uses OAuth 2.0 for authentication with the backend API, ensuring secure access to user-specific data.

## Error Handling

The app gracefully handles API errors:
- 404: Content not found - suggests available alternatives
- 403: Premium content - explains access requirements
- 429: Rate limits - informs about reset periods
- 500: Server errors - provides user-friendly messages

## Development

To extend the app:

1. Update the action manifest when adding new API endpoints
2. Modify the system instructions in config.json to reflect new capabilities
3. Test thoroughly to ensure all skills work as expected
4. Update this README as needed

## Constitutional Compliance

This app maintains strict compliance with the Zero-Backend-LLM architecture:
- All intelligence resides in ChatGPT
- Backend only serves data deterministically
- No LLM processing occurs in the backend
- Content is delivered verbatim from storage