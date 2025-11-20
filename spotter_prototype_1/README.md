# Spotter - Fitness Companion for Boston University

Spotter is a group project focused on improving student wellness at Boston University. Our goal is to create an easy-to-use fitness companion that encourages stronger workout habits, community engagement, and consistent progress tracking. Unlike generic fitness apps, Spotter tailors the experience to BU students by connecting activities, locations, and challenges directly to them.

## Features

1. **New Workout** - Get personalized weightlifting exercise routines based on body parts and specific muscles
2. **Find Class** - Discover fitness classes on or off campus based on your preferences
3. **Log Workout** - Track your workouts with descriptions, photos, and personal records
4. **New Challenge** - Create fitness challenges with friends and track your progress
5. **Find Recipes** - Get meal suggestions based on your fitness goals

## Technology Stack

- **Backend**: Pure Python with Flask
- **Frontend**: HTML, CSS, JavaScript
- **API**: RESTful API endpoints

## Project Structure

```
spotter/
├── backend/
│   └── app.py              # Flask backend server
├── frontend/
│   ├── index.html          # Home page
│   ├── new-workout.html    # Workout suggestion page
│   ├── find-class.html     # Class finder page
│   ├── log-workout.html    # Workout logging page
│   ├── new-challenge.html  # Challenge creation page
│   ├── find-recipes.html   # Recipe finder page
│   ├── profile.html        # User profile page
│   ├── css/
│   │   └── style.css      # Main stylesheet
│   └── js/
│       ├── main.js        # Common utilities
│       ├── new-workout.js
│       ├── find-class.js
│       ├── log-workout.js
│       ├── new-challenge.js
│       └── find-recipes.js
├── requirements.txt        # Python dependencies
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd spotter
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the backend server:**
   ```bash
   cd backend
   python app.py
   ```
   The backend will run on `http://localhost:5000`

4. **Open the frontend:**
   - Open `frontend/index.html` in a web browser
   - Or use a local development server (e.g., `python -m http.server` in the frontend directory)

## API Endpoints

### 1. Weightlifting Suggestions
- **POST** `/api/weightlifting-suggestions`
- Body: `{ "body_parts": ["ARMS", "LEGS"], "muscles": ["biceps", "quadriceps"] }`
- Returns: List of exercises with sets, reps, and rest time

### 2. Exercise Class Suggestions
- **POST** `/api/exercise-class-suggestions`
- Body: `{ "liked_classes": ["CARDIO"], "disliked_classes": [], "distance": "5 miles", "location": "on_campus" }`
- Returns: List of suggested classes

### 3. Log Workout
- **POST** `/api/log-workout`
- Body: `{ "description": "...", "privacy": "public", "photo_url": "...", "personal_record": "..." }`
- Returns: Confirmation message

### 4. Create Challenge
- **POST** `/api/create-challenge`
- Body: `{ "start_date": "MM/DD/YYYY", "end_date": "MM/DD/YYYY", "description": "...", "privacy": "public", "goals": [], "friends": [] }`
- Returns: Challenge details

### 5. Recipe Suggestion
- **POST** `/api/recipe-suggestion`
- Body: `{ "meal_type": "breakfast", "fitness_goal": "lose_weight" }`
- Returns: Recipe details with ingredients and nutrition info

### 6. Get Muscles
- **GET** `/api/muscles?body_part=arms`
- Returns: List of available muscles for a body part

## Use Cases Implemented

1. **Use Case 1**: System provides specific weightlifting suggestions
2. **Use Case 2**: System provides user with exercise class suggestions
3. **Use Case 3**: User logs workout
4. **Use Case 4**: User creates a challenge
5. **Use Case 5**: User receives recipe suggestion

## Design

The application follows a minimalist black and white design matching the provided UI wireframes:
- Bold, uppercase typography
- Rectangular buttons with black borders
- Clean, simple layout
- Mobile-first responsive design
- Consistent header and bottom navigation

## Notes

- The backend uses in-memory storage for simplicity. In production, this should be replaced with a proper database.
- Media uploads are currently simulated. In production, implement proper file upload handling.
- User authentication is simplified. In production, implement proper session management.
- The application is designed for Boston University students and can be extended with BU-specific features.

## Future Enhancements

- Database integration (SQLite, PostgreSQL, etc.)
- User authentication and sessions
- File upload handling for photos/videos
- Real-time location services for class finding
- Integration with external recipe APIs
- Social features for challenges
- Progress tracking and analytics

## License

This project is part of a group project for Boston University.

