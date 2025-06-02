# Prismeet

A next-generation video meeting platform that revolutionizes remote collaboration with advanced recording, AI-powered insights, and seamless post-meeting workflows.

## 🎯 Overview

Prismeet is an enhanced alternative to Riverside.fm, designed to provide crystal-clear video recordings, intelligent meeting summaries, and professional-grade editing capabilities. Built for content creators, remote teams, and businesses who demand the highest quality in their video communications.

## ✨ Key Features

### 🎥 High-Quality Recording System

- **Local + Cloud Storage**: Individual participant videos stored both locally and in the cloud for maximum reliability
- **Progressive Upload**: Seamless background uploading during meetings to prevent data loss
- **Multi-format Support**: Record in various resolutions and formats (4K, 1080p, 720p)
- **Audio Isolation**: Separate audio tracks for each participant for enhanced post-production

### 🎬 Professional Video Compilation

- **Automatic Post-Meeting Processing**: Professional video call layouts generated automatically
- **Smart Transitions**: Intelligent scene switching based on speaker detection
- **Custom Layouts**: Multiple layout options (grid, speaker focus, side-by-side, presentation mode)
- **Brand Integration**: Custom overlays, logos, and branding elements

### ⏰ Flexible Download & Timestamps

- **Precise Segmentation**: Download specific portions of recordings with exact timestamps
- **Multiple Export Formats**: MP4, MOV, WebM, and audio-only options
- **Batch Processing**: Download multiple segments or entire meetings in bulk
- **Quality Selection**: Choose from various quality settings for different use cases

### 🤖 AI-Powered Intelligence

- **Meeting Summaries**: Automatically generated key points, decisions, and action items
- **Speaker Identification**: AI recognizes and labels different speakers
- **Sentiment Analysis**: Track meeting mood and engagement levels
- **Topic Extraction**: Identify and categorize discussion topics

### 🗣️ Real-Time Captions & Translation

- **Live Captioning**: Real-time speech-to-text during meetings
- **Multi-language Support**: Support for 50+ languages
- **Translation Services**: Real-time translation for international teams
- **Caption Export**: Download captions in SRT, VTT, and TXT formats

### ✂️ Advanced Video Editing

- **Built-in Editor**: Professional editing tools directly in the platform
- **Timeline Editing**: Precise cut, trim, and splice capabilities
- **Audio Enhancement**: Noise reduction, echo cancellation, and volume normalization
- **Text Overlays**: Add titles, lower thirds, and custom graphics

### 📁 Smart Storage Management

- **Intelligent Organization**: Automatic categorization by date, participants, and topics
- **Search Functionality**: Advanced search across transcripts, titles, and metadata
- **Storage Analytics**: Track usage and optimize storage costs
- **Archive Management**: Automated archiving of older recordings

## 🏗️ Project Structure

```
prismeet/
├── backend/                 # Backend services and APIs
│   ├── docker-compose.prod.yml
│   └── docker-compose.yml
├── docker/                  # Docker configuration files
├── frontend/               # React-based web application
├── media/                  # Media processing and storage
├── nginx/                  # Nginx configuration for load balancing
├── scripts/                # Deployment and utility scripts
├── static/                 # Static assets and files
└── README.md              # This file
```

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend development)
- FFmpeg (for media processing)
- VSCode (recommended IDE)

### Quick Start with Docker

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/prismeet.git
   cd prismeet
   ```

2. **Start the development environment**

   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Frontend: http://localhost:3000 (Next.js)
   - Backend API: http://localhost:8000 (Django)
   - Admin Panel: http://localhost:8000/admin (Django Admin)
   - Database: PostgreSQL on port 5432

### Production Deployment

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🛠️ Technology Stack

### 🧱 Core Architecture

#### 🔹 Backend

- **Language**: Python 3.11
- **Framework**: Django 4.x
- **API**: Django REST Framework (DRF)
- **Real-time**: Django Channels + Channels Redis
- **Async tasks**: Celery
- **Message broker**: Redis
- **Database**: PostgreSQL (via Docker)
- **Media processing**:
  - FFmpeg (for audio/video encoding)
  - MoviePy (Python video editing)
- **AI / NLP**:
  - HuggingFace Transformers (for summarization/transcription)
  - Torch (for AI model support)
- **Authentication**:
  - Email/password (DRF JWT)
  - Google OAuth (via `social-auth-app-django`)
- **File storage**:
  - Local storage (media/ & static/)
  - Optional: AWS S3 or cloud (via `django-storages`, `boto3`)
- **Security & Settings**: `python-decouple`, `.env` management

#### 🔹 Frontend

- **Language**: TypeScript
- **Framework**: Next.js (React)
- **State management**: React Context / Zustand (optional)
- **Real-time Communication**: WebSockets (via backend Channels)
- **Media access**: WebRTC (browser media APIs)
- **Styling**: Tailwind CSS
- **Bundler**: Vite (optional), Next.js built-in bundler
- **API handling**: Axios or Fetch
- **Authentication**: NextAuth.js or custom JWT handling
- **AI Integration**: Frontend interaction with Django AI endpoints

#### 🐳 Containerization / DevOps

- **Docker**: For isolating backend, frontend, DB
- **Docker Compose**: For orchestrating multi-container setup
- **Production**:
  - `docker-compose.prod.yml` (to be added)
  - Gunicorn for Django serving
  - Nginx reverse proxy (optional later)
- **Environment Variables**: `.env`, `.env.dev`, `.env.prod`

#### 🛠️ Development Tools

- **Package manager**: `pip`, `conda` (for local Python environment)
- **Editor/IDE**: VSCode recommended
- **Linting/Formatting**: Black, isort, flake8
- **Debugging**: Django Debug Toolbar
- **Testing**: Pytest + pytest-django
- **Browser Media Testing**: Chrome DevTools (for camera/mic/webRTC debugging)

## 📋 Development Roadmap

### Phase 1: Core Platform (Q2 2025)

- [ ] Basic video recording and storage
- [ ] User authentication and room management
- [ ] Real-time video calling with WebRTC
- [ ] Basic post-meeting video compilation

### Phase 2: AI Integration (Q3 2025)

- [ ] AI-powered meeting summaries
- [ ] Real-time transcription and captions
- [ ] Speaker identification and diarization
- [ ] Multi-language support

### Phase 3: Advanced Features (Q4 2025)

- [ ] Built-in video editor
- [ ] Advanced analytics and insights
- [ ] API for third-party integrations
- [ ] Mobile applications (iOS/Android)

### Phase 4: Enterprise Features (Q1 2026)

- [ ] SSO and enterprise authentication
- [ ] Advanced admin controls and permissions
- [ ] Custom branding and white-labeling
- [ ] Compliance features (GDPR, HIPAA)

## 🤝 Contributing

We welcome contributions from the community! Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting pull requests.

### Development Setup

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Set up the backend environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py createsuperuser
   ```
4. **Set up the frontend environment**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
5. **Run tests and ensure code quality**

   ```bash
   # Backend tests
   cd backend && pytest

   # Code formatting
   black . && isort . && flake8

   # Frontend tests
   cd frontend && npm run test
   ```

6. **Submit a pull request**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Acknowledgments

- Built with ❤️ by me
- Inspired by the need for better remote collaboration tools
- Thanks to all contributors and the open-source community

---

**Prismeet** - Redefining video meetings for the modern workplace.
