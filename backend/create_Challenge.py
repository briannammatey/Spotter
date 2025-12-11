# Create Challenge Module

from datetime import datetime
import uuid
from data_manager import add_challenge


def validate_challenge_data(data):
    """
    Validate challenge data with challenge type, category, and sanity checks
    """
    errors = []
    
    # Extract and validate challenge type (convert to title case for comparison)
    challenge_type = data.get("challenge_type", "").strip().title()
    if not challenge_type:
        errors.append("Challenge type is required")
    elif challenge_type not in ["Time-Based", "Achievement-Based"]:
        errors.append("Challenge type must be 'Time-Based' or 'Achievement-Based'")
    
    # Extract and validate category (convert to title case for comparison)
    category = data.get("category", "").strip().title()
    if not category:
        errors.append("Category is required")
    elif category not in ["Weightlifting", "Cardio", "Classes"]:
        errors.append("Category must be 'Weightlifting', 'Cardio', or 'Classes'")
    
    # Extract and validate title
    title = data.get("title", "").strip()
    if not title:
        errors.append("Challenge title is required")
    elif len(title) > 100:
        errors.append("Challenge title must be less than 100 characters")
    
    # Extract and validate goal
    goal = data.get("goal", "").strip()
    if not goal:
        errors.append("Goal is required")
    elif len(goal) > 200:
        errors.append("Goal must be less than 200 characters")
    
    # Extract and validate dates
    start_date = data.get("start_date", "").strip()
    end_date = data.get("end_date", "").strip()
    
    if not start_date:
        errors.append("Start date is required")
    if not end_date:
        errors.append("End date is required")
    
    # Validate date logic and sanity checks
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            
            if end <= start:
                errors.append("End date must be after start date")
            
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            if start < today:
                errors.append("Start date cannot be in the past")
            
            # Sanity check: Challenge duration
            duration = (end - start).days
            if duration < 1:
                errors.append("Challenge must be at least 1 day long")
            elif duration > 365:
                errors.append("Challenge duration cannot exceed 1 year (365 days)")
            
        except ValueError:
            errors.append("Invalid date format. Use YYYY-MM-DD")
    
    # Extract and validate description
    description = data.get("description", "").strip()
    if not description:
        errors.append("Challenge description is required")
    elif len(description) < 10:
        errors.append("Description must be at least 10 characters")
    elif len(description) > 1000:
        errors.append("Description must be less than 1000 characters")
    
    # Extract and validate privacy
    privacy = data.get("privacy", "").strip().lower()
    if not privacy or privacy not in ["private", "public"]:
        errors.append("Privacy setting is required (private or public)")
    
    # Validate type-specific fields with sanity checks
    if challenge_type == "Achievement-Based":
        target_value = data.get("target_value")
        metric = data.get("metric", "").strip().lower()

        if target_value is None or target_value == "":
            errors.append("Target value is required for achievement-based challenges")
        else:
            try:
                target = float(target_value)
                if target <= 0:
                    errors.append("Target value must be greater than 0")
                
                # Sanity checks based on category and target value
                if category == "Weightlifting":
                    if metric in ["pounds", "lbs", "kg", "kilograms"]:
                        if target > 1000:
                            errors.append("Weightlifting target seems unrealistic (max: 1000 lbs/kg). Please verify your goal.")
                        elif target < 5:
                            errors.append("Weightlifting target seems too low (min: 5 lbs/kg). Please verify your goal.")
                    elif metric in ["reps", "repetitions"]:
                        if target > 10000:
                            errors.append("Repetition target seems unrealistic (max: 10,000 reps). Please verify your goal.")
                
                elif category == "Cardio":
                    if metric in ["miles", "mi", "kilometers", "km"]:
                        if target > 5000:
                            errors.append("Distance target seems unrealistic (max: 5,000 miles/km). Please verify your goal.")
                        elif target < 0.1:
                            errors.append("Distance target seems too low (min: 0.1 miles/km). Please verify your goal.")
                    elif metric in ["minutes", "hours"]:
                        max_minutes = 100000 if metric == "minutes" else 1500
                        if target > max_minutes:
                            errors.append(f"Time target seems unrealistic (max: {max_minutes} {metric}). Please verify your goal.")
                
                elif category == "Classes":
                    if metric in ["classes", "sessions"]:
                        # Calculate max reasonable classes based on duration
                        if start_date and end_date:
                            try:
                                duration = (datetime.strptime(end_date, "%Y-%m-%d") - 
                                          datetime.strptime(start_date, "%Y-%m-%d")).days
                                max_classes = duration * 2  # Max 2 classes per day
                                if target > max_classes:
                                    errors.append(f"Class target seems unrealistic ({target} classes in {duration} days = {target/duration:.1f} classes/day). Maximum recommended: {max_classes} classes.")
                            except:
                                pass
                        elif target > 1000:
                            errors.append("Class target seems unrealistic (max: 1000 classes). Please verify your goal.")
                
            except (ValueError, TypeError):
                errors.append("Target value must be a valid number")
        
        # Validate metric for achievement-based challenges
        if not metric:
            errors.append("Metric is required for achievement-based challenges (e.g., 'miles', 'pounds', 'classes')")
        elif len(metric) > 50:
            errors.append("Metric must be less than 50 characters")
    
    return len(errors) == 0, errors


def create_challenge(data, creator_email=None):
    """
    Create a new challenge with type and category
    Args:
        data: Challenge data dictionary containing:
            - challenge_type: "Time-Based" or "Achievement-Based"
            - category: "Weightlifting", "Cardio", or "Classes"
            - title, goal, start_date, end_date, description, privacy
            - target_value (for achievement-based): numeric goal
            - metric (for achievement-based): unit of measurement
        creator_email: Email of the user creating the challenge (from auth)
    """
    try:
        # Validate data
        is_valid, errors = validate_challenge_data(data)
        
        if not is_valid:
            return False, {
                "success": False,
                "errors": errors
            }, 400
        
        # Extract validated data (normalize to title case for challenge_type and category)
        challenge_type = data.get("challenge_type", "").strip().title()
        category = data.get("category", "").strip().title()
        title = data.get("title", "").strip()
        goal = data.get("goal", "").strip()
        start_date = data.get("start_date", "").strip()
        end_date = data.get("end_date", "").strip()
        description = data.get("description", "").strip()
        privacy = data.get("privacy", "").strip().lower()
        invited_friends = data.get("invited_friends", [])
        
        # Create base challenge object
        challenge = {
            "id": str(uuid.uuid4()),
            "challenge_type": challenge_type,
            "category": category,
            "title": title,
            "goal": goal,
            "start_date": start_date,
            "end_date": end_date,
            "description": description,
            "privacy": privacy,
            "invited_friends": invited_friends,
            "creator": creator_email or "Anonymous",
            "created_at": datetime.now().isoformat(),
            "participants": 1,
            "type": "challenge"
        }
        
        # Save challenge 
        success = add_challenge(challenge)
        
        if success:
            challenge_response = {k: v for k, v in challenge.items() if k != "_id"}
            
            return True, {
                "success": True,
                "message": "Challenge created successfully!",
                "challenge": challenge_response
            }, 201
        else:
            return False, {
                "success": False,
                "errors": ["Failed to save challenge"]
            }, 500
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False, {
            "success": False,
            "errors": [f"Server error: {str(e)}"]
        }, 500