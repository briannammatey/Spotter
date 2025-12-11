# Spotter 
**Collaborators**: Brianna Matey, Aaron Huang, Anjali Amin, Bidipta Roy
<br>
A fitness app built by students, for students designed specifically for the Boston University community.
Spotter helps students track workouts, join challenges, stay motivated, and build healthier habits through a supportive, campus-centered platform.

## Overview
Spotter is a group project focused on improving student wellness at Boston University. Our goal is to create an easy-to-use fitness companion that encourages stronger workout habits, community engagement, and consistent progress tracking.
Unlike generic fitness apps, Spotter tailors the experience to BU students by connecting activities, locations, and challenges directly to them.

## Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Spotter
```

### 2. Set Up Virtual Environment (Recommended)
```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install flask flask-cors python-dotenv pytest pytest-cov
```

### 4. Set Up Environment Variables
Create a `.env` file in the backend folder and paste in the two API Keys provided in the final deliverable
```bash
PORT=5001
```

## Running the Application

### Start the Flask Server
From the project root directory:

```bash
cd backend
python app.py
```

The server will start on `http://localhost:5001` by default.

You should see output like:
```
============================================================
🐾 SPOTTER SERVER STARTING
============================================================
📁 Serving files from: /path/to/Spotter/frontend
🌐 Open your browser to: http://localhost:5001
🌐 Or try: http://127.0.0.1:5001
============================================================
```

### Access the Application
Open your web browser and navigate to:
- `http://localhost:5001`
- Or `http://127.0.0.1:5001`


## How To Test
Dependencies to install: pytest, coverage, mongomock
<br>
Set your api key for OpenAI feature: $env:OPENAI_API_KEY="your_api_key_here"
<br>
To test run:  python -m pytest -v 
<br>
To run coverage: 
- python -m coverage run -m pytest
- python -m coverage report
- python -m coverage html (To see HTML version)


## Project Structure
```
Spotter/
├── backend/           # Flask backend application
│   ├── app.py        # Main application entry point
│   ├── auth.py       # Authentication logic
│   ├── db.py         # Database operations
│   ├── create_Challenge.py
│   ├── logWorkout.py
│   ├── findClasses.py
│   ├── getExercises.py
│   └── recipeSuggestions/
├── frontend/         # frontend files
├── tests/           # Test suite
│   ├── test_createChallenge.py
│   └── test_logWorkout.py
└── README.md
```
