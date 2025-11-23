# JARVIS 1.0 - Project Structure Blueprint

This document outlines the professional directory structure of the JARVIS 1.0 application.

## Directory Map

```text
JARVIS 1.0/
├── core/                   # Backend Application Logic
│   ├── __init__.py         # Package initialization
│   ├── Gemini.py           # Google Gemini AI integration logic
│   ├── functions.py        # Core utility functions (TTS, STT, System)
│   └── jarvis_engine.py    # Main command processing engine
│
├── docs/                   # Project Documentation
│   ├── LOGIC.md            # Detailed logic flow for AI/Task modes
│   └── SETUP.md            # Installation and setup instructions
│
├── scripts/                # Utility & Maintenance Scripts
│   ├── list_models.py      # Helper to list available AI models
│   └── test_gen.py         # Script to verify AI generation capabilities
│
├── static/                 # Frontend Static Assets
│   ├── css/
│   │   └── style.css       # Main stylesheet
│   ├── images/
│   │   └── jarvis_icon.png # Application icons and assets
│   └── js/
│       └── script.js       # Frontend logic and Socket.IO handling
│
├── templates/              # HTML Templates (Flask)
│   └── index.html          # Main application interface
│
├── tests/                  # Unit & Integration Tests
│   └── test_gemini.py      # Tests for Gemini AI module
│
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore configuration
├── Jarvis.py               # Application Entry Point (Run this file)
├── project_structure.md    # This file
├── README.md               # Main project overview and quick start
└── requirements.txt        # Python dependency list
```

## Module Descriptions

### Root Directory
- **Jarvis.py**: The main entry point for the Flask application. Initializes the server and Socket.IO.
- **requirements.txt**: Lists all Python libraries required to run the project.
- **README.md**: The primary landing page for the project, containing an overview and basic usage.

### Core (`core/`)
Contains the heavy lifting of the application.
- **Gemini.py**: Handles all communication with the Google Gemini API.
- **jarvis_engine.py**: The "brain" that decides how to process user input (Task Mode vs AI Mode).
- **functions.py**: specific implementations of features like speaking, listening, or system commands.

### Static & Templates (`static/`, `templates/`)
Standard Flask structure for serving the web interface.
- **style.css**: Defines the visual theme (Glassmorphism, colors).
- **script.js**: Handles the chat interface, microphone toggling, and real-time events.
- **index.html**: The single-page application layout.

### Documentation (`docs/`)
Supplementary documentation for developers and users.