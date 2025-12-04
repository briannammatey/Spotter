# Log Workout Module

from datetime import datetime
import uuid
from data_manager import add_workout

def validate_workout_data(data):
    """
    Validate workout data
    """
    errors = []
    
    # Extract and validate workout name
    workout_name = data.get("workout_name", "").strip()
    if not workout_name:
        errors.append("Workout name is required")
    elif len(workout_name) > 100:
        errors.append("Workout name must be less than 100 characters")
    
    # Extract and validate date
    workout_date = data.get("date", "").strip()
    if not workout_date:
        errors.append("Workout date is required")
    else:
        try:
            # Validate date format
            datetime.strptime(workout_date, "%Y-%m-%d")
        except ValueError:
            errors.append("Invalid date format. Use YYYY-MM-DD")
    
    # Extract and validate duration
    duration = data.get("duration", "").strip()
    if not duration:
        errors.append("Duration is required")
    else:
        try:
            duration_num = int(duration)
            if duration_num <= 0:
                errors.append("Duration must be greater than 0")
            elif duration_num > 1440:  # 24 hours in minutes
                errors.append("Duration cannot exceed 24 hours (1440 minutes)")
        except ValueError:
            errors.append("Duration must be a valid number")
    
    # Extract and validate workout type
    workout_type = data.get("workout_type", "").strip()
    valid_types = ["cardio", "strength", "flexibility", "sports"]
    if not workout_type:
        errors.append("Workout type is required")
    elif workout_type not in valid_types:
        errors.append(f"Workout type must be one of: {', '.join(valid_types)}")
    
    # Extract and validate intensity level
    intensity = data.get("intensity", "").strip()
    valid_intensities = ["low", "medium", "high"]
    if not intensity:
        errors.append("Intensity level is required")
    elif intensity not in valid_intensities:
        errors.append(f"Intensity must be one of: {', '.join(valid_intensities)}")
    
    # Extract and validate workout notes
    notes = data.get("notes", "").strip()
    if not notes:
        errors.append("Workout notes are required")
    elif len(notes) < 5:
        errors.append("Workout notes must be at least 5 characters")
    elif len(notes) > 1000:
        errors.append("Workout notes must be less than 1000 characters")
    
    # Extract and validate privacy
    privacy = data.get("privacy", "").strip()
    if not privacy or privacy not in ["private", "public"]:
        errors.append("Privacy setting is required (private or public)")

    # Validate calories (optional)
    calories = data.get("calories", "")
    if calories and str(calories).strip():
        try:
            calories_num = int(calories)
            if calories_num < 0:
                errors.append("Calories burned cannot be negative")
            elif calories_num > 10000:
                errors.append("Calories burned seems too high (max 10000)")
        except ValueError:
            errors.append("Calories must be a valid number")
    
    return len(errors) == 0, errors

def log_workout(data, creator_email=None):
    """
    Log a new workout
    Args:
        data: Workout data dictionary
        creator_email: Email of the user logging the workout (from auth)
    """
    try:
        # Validate data
        is_valid, errors = validate_workout_data(data)
        
        if not is_valid:
            return False, {
                "success": False,
                "errors": errors
            }, 400
        
        # Extract validated data
        workout_name = data.get("workout_name", "").strip()
        workout_date = data.get("date", "").strip()
        duration = data.get("duration", "").strip()
        workout_type = data.get("workout_type", "").strip()
        intensity = data.get("intensity", "").strip()
        notes = data.get("notes", "").strip()
        privacy = data.get("privacy", "").strip()
        
        # optional calories field
        calories = data.get("calories", "")
        if calories and str(calories).strip():
            calories = int(calories)
        else:
            calories = None
        
        # Create workout object
        workout = {
            "id": str(uuid.uuid4()),
            "workout_name": workout_name,
            "date": workout_date,
            "duration": int(duration),
            "workout_type": workout_type,
            "intensity": intensity,
            "calories": calories,  
            "notes": notes,
            "privacy": privacy,
            "creator": creator_email or "Anonymous",  # Use authenticated email
            "created_at": datetime.now().isoformat(),
            "type": "workout"
        }
        
        # Save workout 
        success = add_workout(workout)
        
        if success:
            # Remove
            workout_response = {k: v for k, v in workout.items() if k != "_id"}
            
            return True, {
                "success": True,
                "message": "Workout logged successfully!",
                "workout": workout_response
            }, 201
        else:
            return False, {
                "success": False,
                "errors": ["Failed to save workout"]
            }, 500
            
    except Exception as e:
        return False, {
            "success": False,
            "errors": [f"Server error: {str(e)}"]
        }, 500