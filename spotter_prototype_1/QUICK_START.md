# Quick Start Guide - Spotter

## Important: Backend Server Must Be Running!

The Profile page requires the backend server to be running. If you see "Error loading workouts/challenges", it means the backend server is not running.

## Steps to Run the Application:

### 1. Start the Backend Server

Open a terminal and run:

```bash
cd backend
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5001
```

**Keep this terminal window open!** The server must stay running.

### 2. Open the Frontend

In a new terminal or browser:

**Option A: Direct file opening**
- Open `frontend/index.html` in your web browser

**Option B: Using a local server (recommended)**
```bash
cd frontend
python -m http.server 8000
```
Then open `http://localhost:8000` in your browser

### 3. Test the Application

1. Go to "Log Workout" page
2. Fill in the description (required)
3. Optionally add a photo and personal record
4. Click "Save To Profile"
5. Navigate to the Profile page (bottom right icon)
6. Your workout should appear!

### Troubleshooting

**If you see "Error loading workouts":**
- Make sure the backend server is running (step 1)
- Check the browser console (F12) for error messages
- Verify the backend is running on `http://localhost:5001`

**If workouts don't appear after saving:**
- Make sure you clicked "Save To Profile" (not "Post To Feed")
- Click the REFRESH button on the Profile page
- Check that the backend server is still running

**Note:** Data is stored in memory, so if you restart the backend server, all saved workouts and challenges will be lost. This is expected behavior for the current implementation.

