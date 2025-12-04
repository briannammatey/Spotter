# backend/auth.py

from typing import Tuple, Dict, Any, Optional
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from db import users, sessions


def _is_bu_email(email: str) -> bool:
    return email.lower().endswith("@bu.edu")


def _create_session(email: str) -> str:
    """Create a new session token for the user"""
    token = str(uuid.uuid4())
    
    # Session expires in 7 days
    expiry = datetime.now() + timedelta(days=7)
    
    sessions.insert_one({
        "token": token,
        "email": email,
        "created_at": datetime.now(),
        "expires_at": expiry
    })
    
    return token


def validate_token(token: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a session token.
    Returns (is_valid, email_or_none)
    """
    if not token:
        return False, None
    
    session = sessions.find_one({"token": token})
    
    if not session:
        return False, None
    
    # Check if expired
    if datetime.now() > session["expires_at"]:
        # Remove expired session
        sessions.delete_one({"token": token})
        return False, None
    
    return True, session["email"]


def logout_user(token: str) -> Tuple[bool, Dict[str, Any], int]:
    """Remove the session token"""
    if not token:
        return False, {"success": False, "error": "No token provided"}, 400
    
    sessions.delete_one({"token": token})
    
    return True, {"success": True, "message": "Logged out successfully"}, 200


def register_user(email: str, password: str) -> Tuple[bool, Dict[str, Any], int]:
    """
    Register a new user with a BU email and hashed password.
    Returns (success, response_body, status_code)
    """
    if not email or not password:
        return False, {"success": False, "error": "Email and password are required."}, 400

    email = email.strip().lower()

    if not _is_bu_email(email):
        return False, {
            "success": False,
            "error": "Only BU emails (@bu.edu) are allowed."
        }, 400

    # Check if user already exists
    if users.find_one({"email": email}):
        return False, {
            "success": False,
            "error": "An account with this email already exists."
        }, 400

    if len(password) < 6:
        return False, {
            "success": False,
            "error": "Password must be at least 6 characters long."
        }, 400

    password_hash = generate_password_hash(password)

    users.insert_one({
        "email": email,
        "password_hash": password_hash,
        "created_at": datetime.now()
    })

    # Create session
    token = _create_session(email)

    return True, {
        "success": True,
        "message": "User registered successfully.",
        "token": token,
        "email": email,
    }, 201


def login_user(email: str, password: str) -> Tuple[bool, Dict[str, Any], int]:
    """
    Log in an existing user. Validates email & password.
    Returns (success, response_body, status_code)
    """
    if not email or not password:
        return False, {"success": False, "error": "Email and password are required."}, 400

    email = email.strip().lower()
    user = users.find_one({"email": email})

    if not user:
        return False, {"success": False, "error": "Invalid email or password."}, 401

    if not check_password_hash(user["password_hash"], password):
        return False, {"success": False, "error": "Invalid email or password."}, 401

    # Create session
    token = _create_session(email)

    return True, {
        "success": True,
        "message": "Login successful.",
        "token": token,
        "email": email,
    }, 200
