# Course Companion Web Frontend

This is the web frontend for the Course Companion FTE - Hackathon IV project. It provides a user interface for the AI Agent Development course, allowing students to browse modules, track progress, and engage with course content.

## Overview

The web frontend is built with:
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful icon library
- **SWR** - React Hooks for data fetching

## Features

- **Course Modules**: Browse and access course modules
- **Progress Tracking**: Visualize learning progress and achievements
- **Responsive Design**: Works on all device sizes
- **Authentication**: User login and signup functionality
- **Content Display**: Render course content in an engaging way

## Architecture

The frontend follows a clean architecture pattern:

```
src/
├── app/                 # Next.js App Router pages
│   ├── layout.tsx       # Root layout with providers
│   ├── page.tsx         # Homepage
│   └── modules/         # Modules page
├── components/          # Reusable UI components
│   ├── Header.tsx       # Navigation header
│   ├── Footer.tsx       # Page footer
│   ├── CourseCard.tsx   # Module display card
│   └── ProgressOverview.tsx # Progress visualization
├── lib/                 # Shared utilities
│   ├── auth.tsx         # Authentication context
│   └── api.ts           # API client
└── styles/              # Global styles
    └── globals.css      # Tailwind and custom styles
```

## Zero-Backend-LLM Compliance

This frontend maintains strict compliance with the Zero-Backend-LLM architecture:
- All intelligence remains in the ChatGPT app
- Frontend only displays data fetched from the backend API
- No LLM processing occurs in the frontend
- Backend serves content verbatim without transformation

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create a `.env.local` file:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Environment Variables

- `NEXT_PUBLIC_API_BASE_URL` - Base URL for the backend API (default: http://localhost:8000/api/v1)

## Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## API Integration

The frontend communicates with the backend API through the `apiClient` utility. All API endpoints are mapped according to the specification:

### Content Delivery
- `GET /chapters/{id}` - Get chapter content
- `GET /chapters` - List chapters
- `GET /modules/{id}` - Get module overview

### Progress Tracking
- `GET /progress/{userId}` - Get user progress
- `PUT /progress/{userId}/chapters/{id}` - Mark chapter complete
- `GET /progress/{userId}/streak` - Get learning streak

### Quizzes
- `GET /quizzes` - List available quizzes
- `POST /quizzes/{id}/start` - Start quiz attempt
- `POST /quizzes/{id}/submit` - Submit quiz answers

## Components

### Header
Responsive navigation header with logo, navigation links, and user authentication controls.

### Footer
Site-wide footer with links to important pages and legal information.

### CourseCard
Displays course module information with progress indicators and difficulty levels.

### ProgressOverview
Visualizes user's learning progress with key metrics.

## Authentication

The frontend implements a complete authentication flow:
- User login and signup
- Session management
- Protected routes
- Tier-based content access

## Styling

- Uses Tailwind CSS for utility-first styling
- Responsive design for all screen sizes
- Consistent color scheme and typography
- Accessible UI components

## Development

### Adding New Pages

1. Create a new directory in `src/app/`
2. Add a `page.tsx` file
3. Implement the page component
4. Add any required components to `src/components/`

### Adding New Components

1. Create a new file in `src/components/`
2. Export the component as a named export
3. Import and use in other components

### API Integration

1. Add new endpoints to the `ApiClient` class in `src/lib/api.ts`
2. Use the API client in components with SWR for caching and revalidation
3. Handle loading and error states appropriately

## Testing

TODO: Add testing setup with Jest and React Testing Library

## Deployment

The app is ready for deployment to platforms like Vercel, Netlify, or any Node.js hosting service.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is part of the Course Companion FTE - Hackathon IV and follows the project's licensing terms.