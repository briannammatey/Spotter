# Create Challenge Module

from datetime import datetime
import uuid
from data_manager import add_challenge


def validate_challenge_data(data):
    """
    Validate challenge data
    """
    errors = []
    
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
    
    # Validate date logic
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            
            if end <= start:
                errors.append("End date must be after start date")
            
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            if start < today:
                errors.append("Start date cannot be in the past")
                
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
    privacy = data.get("privacy", "").strip()
    if not privacy or privacy not in ["private", "public"]:
        errors.append("Privacy setting is required (private or public)")
    
    return len(errors) == 0, errors

def create_challenge(data, creator_email=None):
    """
    Create a new challenge
    Args:
        data: Challenge data dictionary
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
        
        # Extract validated data
        title = data.get("title", "").strip()
        goal = data.get("goal", "").strip()
        start_date = data.get("start_date", "").strip()
        end_date = data.get("end_date", "").strip()
        description = data.get("description", "").strip()
        privacy = data.get("privacy", "").strip()
        invited_friends = data.get("invited_friends", [])
        
        # Create challenge object
        challenge = {
            "id": str(uuid.uuid4()),
            "title": title,
            "goal": goal,
            "start_date": start_date,
            "end_date": end_date,
            "description": description,
            "privacy": privacy,
            "invited_friends": invited_friends,
            "creator": creator_email or "Anonymous",  # Use authenticated email
            "created_at": datetime.now().isoformat(),
            "participants": 1,  # Creator is first participant
            "type": "challenge"
        }
        
        # Save challenge 
        success = add_challenge(challenge)
        
        if success:
            # Remove 
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
        return False, {
            "success": False,
            "errors": [f"Server error: {str(e)}"]
        }, 500